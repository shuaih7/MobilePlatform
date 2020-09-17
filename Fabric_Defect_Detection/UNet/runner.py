import tensorflow as tf
import os
from datetime import date

from hparams import ModelHparams
from unet import UNet
from utils.losses import AdaptiveLoss
from utils.metrics import IOUScore
from utils.callbacks import MonitorCallback
from utils.visualize import visualize

from dataset.oih_dataset import load_defect, preprocess_train, preprocess_test


class Runner:
    def __init__(
            self,
            # directory params
            data_root='../dataset/oih_stitch_skipping',  # data root
            checkpoint_dir='../results/checkpoint_dir/weights_{epoch:02d}',  # model checkpoint filepath
            monitor_save_dir='../results',
            tensorboard_log_dir='../results/training_logs',

            # model params
            input_format='channels_last',
            compute_format='channels_last',
            n_channels=1,
            activation_fn='relu',
            weight_init_method='he_normal',
            model_variant='tinyUNet',
            input_shape=(512, 512, 1),
            mask_shape=(512, 512, 1),
            input_normalization_method='zero_one',

            # training params
            augment_data=None,
            loss_fn_name=None,
    ):
        self.data_root = data_root
        self.checkpoint_dir = checkpoint_dir
        self.monitor_save_dir = monitor_save_dir
        self.tensorboard_log_dir = tensorboard_log_dir
        if not os.path.exists(self.data_root):
            os.makedirs(self.data_root)
        # if not os.path.exists(self.checkpoint_dir):
        #     os.makedirs(self.checkpoint_dir)
        if not os.path.exists(self.monitor_save_dir):
            os.makedirs(self.monitor_save_dir)
        if not os.path.exists(self.tensorboard_log_dir):
            os.makedirs(self.tensorboard_log_dir)

        self.model_hparams = ModelHparams(
            input_format,
            compute_format,
            n_channels,
            activation_fn,
            weight_init_method,
            model_variant,
            input_shape,
            mask_shape,
            input_normalization_method
        )

        # init model
        unet = UNet(
            input_format=self.model_hparams.input_format,
            compute_format=self.model_hparams.compute_format,
            n_output_channels=1,
            unet_variant=self.model_hparams.model_variant,
            weight_init_method=self.model_hparams.weight_init_method,
            activation_fn=self.model_hparams.activation_fn
        )

        self.model = unet.model

        # TODO: init dataset
        self.init_dataset()

    def init_dataset(self):
        # train set
        train_images, train_masks = load_defect(self.data_root, mode='train')
        train = tf.data.Dataset.from_tensor_slices((train_images, train_masks))
        train = train.shuffle(len(train_images)).map(preprocess_train)
        self.train_set = train.batch(16).repeat()

        # validation set
        valid_images, valid_masks = load_defect(self.data_root, mode='valid')
        valid = tf.data.Dataset.from_tensor_slices((valid_images, valid_masks))
        valid = valid.shuffle(len(valid_images)).map(preprocess_train)
        self.valid_set = valid.batch(len(valid_images))

        # TODO: init test set
        test_images, test_masks = load_defect(self.data_root, mode='test')
        test = tf.data.Dataset.from_tensor_slices((test_images, test_masks))
        test = test.map(preprocess_test)
        self.test_set = test.batch(len(test_images))

    def train(self):
        # TODO: pass in train params
        if not os.path.exists(self.checkpoint_dir):
            os.makedirs(self.checkpoint_dir)

        # optimizer
        optimizer = tf.keras.optimizers.Adam()
        self.model.compile(
            optimizer=optimizer,
            loss=AdaptiveLoss(switch_at_threshold=0.3, loss_type='jaccard'),
            metrics=[IOUScore(threshold=0.5)]
        )

        # callbacks
        cp_callback = tf.keras.callbacks.ModelCheckpoint(
            filepath=self.checkpoint_dir,
            save_weights_only=True,
            verbose=1
        )

        tb_callback = tf.keras.callbacks.TensorBoard(
            log_dir=self.tensorboard_log_dir,
            write_graph=True,
            update_freq='epoch'
        )

        mt_callback = MonitorCallback(
            dataset=self.valid_set,
            save_dir=self.monitor_save_dir,
            monitor_freq=3
        )

        # start training...
        self.model.fit(
            self.train_set,
            epochs=300,
            steps_per_epoch=100,
            callbacks=[cp_callback, tb_callback, mt_callback],
            validation_data=self.valid_set,
            validation_steps=None
        )

    def test(self, checkpoint):
        self.model.load_weights(checkpoint)
        for (test_images, test_masks) in self.test_set.take(1):
            predicted_masks = self.model.predict(
                x=test_images,
                batch_size=64,
                verbose=1
            )
            save_dir = os.path.join(self.monitor_save_dir, 'fake_testing')
            visualize(test_images, test_masks, predicted_masks, save_dir)

    def save_model(self, checkpoint, save_dir):
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        self.model.load_weights(checkpoint)
        tf.keras.models.save_model(
            self.model,
            save_dir,
        )
        print('saved model to', save_dir)


if __name__ == '__main__':
    training = False
    if training:
        today = date.today()
    else:
        today = '2020-01-18'
    checkpoint_dir = os.path.join('../results/checkpoint_date/', str(today))
    # if not os.path.exists(checkpoint_dir):
    #     os.makedirs(checkpoint_dir)
    checkpoint_dir = os.path.join(checkpoint_dir, 'weights_{epoch:02d}')
    runner = Runner(checkpoint_dir=checkpoint_dir)
    runner.model.summary()
    # runner.train()

    # test_model_weights = os.path.join('../results/checkpoint_date', '2020-01-18', 'weights_23')
    # runner.test(test_model_weights)

    # save model for tf-serving
    model_save_dir = '../UNet/saved_model'
    save_model_weights = os.path.join('../results/checkpoint_date', '2020-01-18', 'weights_23')
    # runner.test(save_model_weights)
    runner.save_model(save_model_weights, model_save_dir)


