import tensorflow as tf
import os
from utils.visualize import visualize


class MonitorCallback(tf.keras.callbacks.Callback):
    def __init__(self, dataset, save_dir, monitor_freq=5):
        super(MonitorCallback, self).__init__()
        self.dataset = dataset
        self.save_dir = save_dir
        self.monitor_freq = monitor_freq

    def on_epoch_end(self, epoch, logs=None):
        if epoch % self.monitor_freq == 0:
            dataset = self.dataset
            for images, masks in dataset.take(1):
                # input_images = tf.expand_dims(images, axis=0)
                # input_masks = tf.expand_dims(tf.image.resize(masks, [64, 64]), axis=0)

                input_images = images
                input_masks = masks

                predicted_masks = self.model.predict(input_images)
                save_dir = os.path.join(self.save_dir, 'training_epoch-{}'.format(epoch))
                visualize(input_images, input_masks, predicted_masks, save_dir)

        print ('\nSample Prediction after epoch {}\n'.format(epoch+1))