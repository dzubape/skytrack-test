#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, getopt, os

from NetModel import last_train_start, save_model, load_model

from keras.preprocessing.image import ImageDataGenerator
from keras.applications.mobilenet_v2 import MobileNetV2
from keras.models import Model
from keras.layers import Dense, Flatten, Dropout
from keras import optimizers

train_generator=None
test_generator=None
model=None


def build_model(input_shape):    
    # Подгружаем pretrained-сеть
    # но без FFNN-сегмента
    mobnet = MobileNetV2(
        input_shape=input_shape,
        weights='imagenet',
        include_top=False
    )

    # Замораживаем CNN-слои
    for layer in mobnet.layers[:]:
        layer.trainable = False
        
    # Добавляем кастомные слои FFNN
    x = mobnet.output
    x = Flatten()(x)
    x = Dense(1024, activation="relu")(x)
    x = Dropout(0.4)(x)
    x = Dense(256, activation="relu")(x)
    predic = Dense(2, activation="softmax")(x)

    # Создаём общую модель
    model = Model(inputs=mobnet.input, outputs=predic)


def create_generator(mode, ds_dir, input_shape, batch_size):
    if mode == "train":
        generator = ImageDataGenerator(
            rescale=1./255,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True
        )
    elif mode == "test":
        generator = ImageDataGenerator(
            rescale=1./255
        )

    return generator.flow_from_directory(
        ds_dir,
        target_size=input_shape,
        batch_size=batch_size,
        class_mode='categorical'
    )


def fit_catdog(model, train_generator, epoch_count=20, thread_count=3, test_generator=None):
    assert epoch_count > 0
    
    from keras.callbacks import TensorBoard
    
    start_time = last_train_start.update()
    log_path="logs/catdog-{}".format(start_time)

    print("train start time:", start_time)
    print("log dir:", log_path)
    
    tensorboard = TensorBoard(log_dir=log_path)
    model.fit_generator(
        generator=train_generator,
        steps_per_epoch=80,
        epochs=epoch_count,
        validation_data=test_generator,
        validation_steps=10,
        use_multiprocessing=True,
        workers=thread_count,
        callbacks=[tensorboard]
    )
    
    #save_model(model, start_time)


def print_help():
    print("Help yourself!")


def main(argv):
    ds_dir = "cats_vs_dogs_v2"
    train_dir = os.path.join(ds_dir, "train")
    test_dir = os.path.join(ds_dir, "test")
    input_shape = (224, 224, 3)
    batch_size=16
    batch_size=32
    
    global model, train_generator, test_generator
        
    task = None
    model_mark = None
    train_epoch_count = None
    ds_dir=None

    argv = [str(arg) if not None else None for arg in argv]

    try:
        opts, args = getopt.getopt(argv, "htue:m:", [
            "train",
            "use",
            "train-epoch-count=",
            "model-mark="
        ])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
        
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt in ("-t", "--train"):
            ds_dir = train_dir
            task = "train"
        elif opt in ("-u", "--use"):
            task = "use"
            print("Use mode is not implemented yet")
            sys.exit(0)
        elif opt in ("-e", "--train-epoch-count"):
            train_epoch_count = int(arg)
        elif opt in ("-m", "--model-mark"):
            model_mark = arg
            
        if task is None:
            sys.exit(2)

    # flow-генератор данный для тренировки сети
    if train_generator is None:
        train_generator = create_generator(
            "train",
            ds_dir=train_dir,
            input_shape=input_shape[:2],
            batch_size=batch_size
        )

    # flow-генератор данных для валидации
    if test_generator is None:
        test_generator = create_generator(
            "test",
            ds_dir=test_dir,
            input_shape=input_shape[:2],
            batch_size=batch_size
        )

    # Создаём или подгружаем и компилируем модель
    while True:
        if model_mark is not None:
            # Загружаем ранее созданную и обученную модуль
            model = load_model(model_mark)
        elif model is None:
            # Создаём модель на основе MobileNetV2
            model = build_model(input_shape)
        else:
            # Пользуемся уже созданной/загруженной моделью
            break
        
        if task == "train":
            # Алгоритм оптимизации
            learning_rate = 0.0001
            momentum = 0.9
            optimizer = optimizers.SGD(
                lr=learning_rate,
                momentum=momentum
            )
            
            # Компилируем модель
            model.compile(
                loss = "categorical_crossentropy",
                optimizer = optimizer,
                metrics=["accuracy"]
            )
        break


    # Собственно, обучение сети
    fit_catdog(
        model,
        train_generator=train_generator,
        epoch_count=train_epoch_count,
        test_generator=test_generator
    )
    
    save_model(model, last_start_time())
    

if __name__ == '__main__':
    main(sys.argv[1:])
