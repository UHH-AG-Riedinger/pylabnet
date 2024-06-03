import os
import time
import numpy as np
import cv2
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
from skimage.io import imread

import pylabnet.utils.logging.logger as lg
import pylabnet.utils.helper_methods as hm
from PIL import Image
from brisque import BRISQUE


class FocusOptimizer:

    def __init__(self, EAF, Camera, logger, Laser, template_path):
        self.EAF = EAF
        self.Camera = Camera
        self.logger = logger
        self.Laser = Laser
        template = np.mean(imread(template_path), axis=2).astype(np.uint8)
        orig_height, orig_width = template.shape[:2]
        target_height = 2000#360#2000
        fy = target_height / orig_height
        fx = fy
        self.template = cv2.resize(template, None, fx=fx, fy=fy, interpolation=cv2.INTER_AREA)
        self.logger.info(f"Template image loaded and resized from {template_path}")

    def picture_quality_for_focus(self, image, turn=False):
        self.logger.info("Calculating Laplacian variance for picture quality")
        if turn:
            image = np.rot90(image, k=3)
        image_filtered = cv2.medianBlur(image, 3)
        max_value = image_filtered.max()

        laplacian = cv2.Laplacian(image_filtered, cv2.CV_64F)

        # #image_filtered = int(image_filtered / max_value * 255
        # aktuelle_gesamtintensität = np.sum(laplacian)
        # # Zielintensität
        # laplacian = laplacian - np.min(laplacian)
        # zielintensität = 60000000  # Beispielwert
        # # Skalierungsfaktor berechnen
        # skalierungsfaktor = zielintensität / aktuelle_gesamtintensität
        # # Bildintensitäten anpassen
        # neues_bild = laplacian * skalierungsfaktor
        # #print(aktuelle_gesamtintensität)
        # #print(max_value)

        laplacian_variance = laplacian.var() / (max_value**2)
        self.logger.info(f"Laplacian Variance: {laplacian_variance}")
        return laplacian_variance, laplacian

    def picture_quality_sobel(self, image, turn=False):
        self.logger.info("Calculating Sobel magnitude for picture quality")
        if turn:
            image = np.rot90(image, k=3)
        image_filtered = cv2.medianBlur(image, 9)
        sobel_x = cv2.Sobel(image_filtered, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(image_filtered, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        sharpness = magnitude.var() / (magnitude.max()**2)
        return sharpness, image_filtered

    def picture_quality_found_7_score(self, image, scale=1.0):
        self.logger.info(f"Performing template matching with scale {scale}")
        resized_template = cv2.resize(self.template, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        if image.shape[0] < resized_template.shape[0] or image.shape[1] < resized_template.shape[1]:
            self.logger.warning("Resized template is larger than the image. Skipping template matching.")
            return None

        image = cv2.medianBlur(image, 3)
        #image_lap = cv2.Laplacian(image, cv2.CV_64F)
        #image_lap= image_lap - np.min(image_lap)
        #image_lap = image_lap / np.max(image_lap)
        #image_lap = np.uint8(image_lap * 255)

        resized_template = cv2.medianBlur(resized_template, 3)
        #resized_template_lap = cv2.Laplacian(resized_template, cv2.CV_64F)
        #rezized_template_lap = rezized_template_lap - np.min(rezized_template_lap)
        #rezized_template_lap = rezized_template_lap / np.max(rezized_template_lap)
        #resized_template_lap = np.uint8(resized_template_lap * 255)
        #print(rezized_template_lap)
        #figure, ax = plt.subplots(1, 2)
        #ax[0].imshow(image_lap, cmap='gray')
        #ax[1].imshow(rezized_template_lap, cmap='gray')
        #plt.show()

        res = cv2.matchTemplate(image, resized_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        w, h = resized_template.shape[::-1]
        self.logger.info(f"Template matching score: {max_val} at location: {max_loc}")
        return max_val, image

    def picture_quality_Brisque(self, image, turn=False):
        self.logger.info("Calculating BRISQUE score for picture quality")
        if turn:
            image = np.rot90(image, k=3)
        image = np.uint8(image)
        brisque = BRISQUE()
        #score = brisque.score(image)
        quality = brisque.get_score(image)
        self.logger.info(f"BRISQUE score: {quality}")
        return quality, image

    def get_latest_image(self, dirpath, valid_extensions=('jpg', 'jpeg', 'png')):
        self.logger.info(f"Fetching the latest image from directory: {dirpath}")
        valid_files = [os.path.join(dirpath, f) for f in os.listdir(dirpath)
                       if os.path.isfile(os.path.join(dirpath, f)) and f.rsplit('.', 1)[-1] in valid_extensions]
        if not valid_files:
            error_msg = f"No valid images in {dirpath}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        latest_file = max(valid_files, key=os.path.getctime)
        self.logger.info(f"Latest image fetched: {latest_file}")
        return latest_file

    def _template_matching_for_scale(self, image, scale=1.0):
        self.logger.info(f"Performing template matching with scale {scale}")
        resized_template = cv2.resize(self.template, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        if image.shape[0] < resized_template.shape[0] or image.shape[1] < resized_template.shape[1]:
            self.logger.warning("Resized template is larger than the image. Skipping template matching.")
            return None

        res = cv2.matchTemplate(image, resized_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        w, h = resized_template.shape[::-1]
        self.logger.info(f"Template matching score: {max_val} at location: {max_loc}")
        return image[max_loc[1]:max_loc[1] + h, max_loc[0]:max_loc[0] + w]

    def optimize_focus(self, experimet_name, initial_position=None, plot=False):
        if initial_position is None:
            initial_position = self.EAF.EAFget_position()

        positions = np.arange(initial_position - 2000, initial_position + 2000, 100)
        metrics = []

        line1_data = []
        line2_data = []
        line3_data = []
        line4_data = []
        line5_data = []

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        image_slices = []
        line1, = ax1.plot([], [], 'r-', label='Linie 1')
        line2, = ax1.plot([], [], 'b-', label='Linie 2')
        line3, = ax1.plot([], [], 'g-', label='Linie 3')
        line4, = ax1.plot([], [], 'y-', label='Linie 4')
        line5, = ax1.plot([], [], 'm-', label='Linie 5')

        for position in positions:
            self.EAF.EAFmove(position)
            self.logger.info(f"Moving EAF to position {position}")
            while self.EAF.EAFis_moving():
                time.sleep(0.1)

            self.logger.info("Taking picture with camera")
            self.Camera.take_picture(experimet_name)
            image_dir = f"C:/GithubSync/pictures taken/{experimet_name}"
            time.sleep(0.1)
            image_path = self.get_latest_image(image_dir)
            image = cv2.imread(image_path)
            image = image[:, :, 1]    # Roten Kanal extrahieren
            found = self._template_matching_for_scale(image)

            # Bildgröße ermitteln
            image = Image.fromarray(found)
            width, height = image.size

            # Höhe eines Schnitts berechnen
            slice_height = height // 5

            # Für jeden Schnitt das Bild aufteilen und speichern
            for i in range(5):
                # Bereich des Schnitts definieren (links, oben, rechts, unten)
                box = (0, i * slice_height, width, (i + 1) * slice_height)

                # Bildausschnitt erzeugen
                slice = image.crop(box)

                # Bildausschnitt zur Liste hinzufügen
                quality, analysed_image = self.picture_quality_Brisque(slice)

                if i == 0:
                    line1_data.append(quality)
                elif i == 1:
                    line2_data.append(quality)
                elif i == 2:
                    line3_data.append(quality)
                elif i == 3:
                    line4_data.append(quality)
                elif i == 4:
                    line5_data.append(quality)

            if found is None:
                self.logger.warning(f"Template matching failed for position {position}")
                continue

            #quality, analysed_image = self.picture_quality_Brisque(found)
            metrics.append(quality)

            if plot:
                plt.subplot(1, 2, 1)
                ax2.imshow(analysed_image, cmap='gray')
                plt.pause(0.05)

                plt.subplot(1, 2, 2)
                ax1.plot(positions[:len(line1_data)], line1_data)
                ax1.plot(positions[:len(line2_data)], line2_data)
                ax1.plot(positions[:len(line3_data)], line3_data)
                ax1.plot(positions[:len(line4_data)], line4_data)
                ax1.plot(positions[:len(line5_data)], line5_data)
                #plt.plot(positions[:len(metrics)], metrics, 'o', label='Original data')
                plt.pause(0.05)

        f = interp1d(positions, metrics, kind='cubic', fill_value="extrapolate")
        fine_positions = np.linspace(positions[0], positions[-1], num=10000)
        fine_metrics = f(fine_positions)
        max_position = int(fine_positions[np.argmax(fine_metrics)])

        if max_position <= positions[0] or max_position >= positions[-1]:
            if initial_position + 1000 >= 60000 or initial_position - 1000 <= 0:
                self.logger.info("Optimized focus is at edge of search range. No further search possible.")
                return initial_position
            range_adjustment = 5000 if max_position >= positions[-1] else -5000
            return self.optimize_focus(experimet_name, initial_position + range_adjustment, plot)

        self.logger.info(f"Moving EAF to optimized position {max_position}")
        self.EAF.EAFmove(max_position)

        if plot:
            plt.figure()
            plt.plot(positions, metrics, 'o', label='Original data')
            plt.plot(fine_positions, fine_metrics, '-', label='Interpolated curve')
            plt.xlabel('EAF Position')
            plt.ylabel('Picture Quality')
            plt.title('Focus Optimization')
            plt.legend()
            plt.show()

        self.logger.info(f"Optimized focus at position {max_position}")
        return max_position


# Usage example:
logger = lg.LogClient()
galvo = hm.autoconnect_device(device_tag='Arduino_Galvo', logger=logger)
ZWOCamera = hm.autoconnect_device(device_tag='ZWOCamera', logger=logger)
nktLaser = hm.autoconnect_device(device_tag='white_laser', logger=logger)
EAF = hm.autoconnect_device(device_tag='EAF_Telescope', logger=logger)

initial_position = 13000
EAF.EAFmove(initial_position)
while EAF.EAFis_moving():
    time.sleep(0.1)

experiment_name = "Testingwithfocus"
template_path = "C:/GithubSync/8.png"
optimizer = FocusOptimizer(EAF, ZWOCamera, logger, nktLaser, template_path)
optimizer.optimize_focus(experiment_name, plot=True)
