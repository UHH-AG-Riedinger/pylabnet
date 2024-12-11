import os
import time
import numpy as np
import cv2
from matplotlib import pyplot as plt
import matplotlib
from scipy.interpolate import interp1d
from skimage.io import imread

import json

import torch
import torch.nn.functional as F
from torchvision import transforms
from tqdm import tqdm
from multiprocessing import Process

import tkinter as tk
from tkinter import filedialog
from PIL import Image

import pylabnet.utils.logging.logger as lg
import pylabnet.utils.helper_methods as hm
from PIL import Image
from brisque import BRISQUE
from datetime import datetime
#matplotlib.use('SVG')


def plot_subprocess(positions, metrics, found, ax_big, fig, gs, counter):
    pid = os.fork()
    if pid == 0:  # Child process
        plotGraph(positions, metrics, found, ax_big, fig, gs, counter)
        os._exit(0)  # Ensure the child process exits after plotting
    elif pid > 0:  # Parent process
        # Optionally handle background operations, such as logging or waiting
        os.wait()  # Wait for the child process to complete if necessary
    else:
        print("Fork failed!")


def plotGraph(positions, metrics, found, ax_big, fig, gs, counter):
    ax_big.clear()
    ax_big.plot(positions[:len(metrics)], metrics, 'o', label='Original data')
    #plt.subplot(1, 3, 3)
    #axs[1].imshow(found, cmap='gray')
    plt.pause(0.005)
    #plt.subplot(1, 2, 2)
    ax = fig.add_subplot(gs[1, counter])
    ax.imshow(found, cmap='gray')
    plt.tight_layout()
    plt.pause(0.005)
    #plt.ion()  # Turn on interactive mode
    #plt.show(block=True)


class FocusOptimizer:

    def __init__(self, EAF, galvo, Camera, logger, Laser, template_path, pos_laser=[512, 512]):
        self.EAF = EAF
        self.galvo = galvo
        self.Camera = Camera
        self.logger = logger
        self.Laser = Laser
        self.pos_laser = pos_laser
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
        max_valuelap = laplacian.max()
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
        print(max_value)
        print(max_valuelap)
        laplacian_variance = laplacian.var()
        self.logger.info(f"Laplacian Variance: {laplacian_variance}")
        return laplacian_variance, laplacian

    def picture_quality_sobel(self, image, turn=False):
        self.logger.info("Calculating Sobel magnitude for picture quality")
        if turn:
            image = np.rot90(image, k=3)
        image_filtered = image
        max_var = image_filtered.var()
        sobel_x = cv2.Sobel(image_filtered, cv2.CV_64F, 1, 0, ksize=-1)
        sobel_y = cv2.Sobel(image_filtered, cv2.CV_64F, 0, 1, ksize=-1)
        magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        sharpness = magnitude.var() / (max_var)

        laplacian = cv2.Laplacian(image_filtered, cv2.CV_64F)
        max_valuelap = laplacian.max()

        advancedsobel = sharpness * laplacian.var()

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

    def picture_quality_sobel_Konstantin(self, image, turn=False):
        # Get x-gradient in "sx"
        sx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=-1)
        sy = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=-1)
        # Get square root of sum of squares
        sobel = np.hypot(sx, sy)
        print(type(sobel))
        print(type(image))
        sobel_normalized = cv2.normalize(sobel, None, 0, 255, cv2.NORM_MINMAX)
        threshold = 50
        count = np.sum(sobel_normalized > threshold)
        #image_filtered = cv2.medianBlur(sobel_normalized, 3)        imagesum = np.sum(sobel)
        min_element = int(np.min(sobel_normalized))
        max_element = int(np.max(sobel_normalized))
        #plt.figure()
        #plt.hist(sobel, bins=range(min_element, max_element + 2), align='left', edgecolor='black')
        #plt.show()

        return count, image

    def picture_quality_sobel_Konstantin2(self, image, turn=False):
        # Get x-gradient in "sx"
        #image = cv2.medianBlur(image, 3)
        sx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=-1)
        sy = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=-1)
        # Get square root of sum of squares
        sobel = np.hypot(sx, sy)

        sobel_normalized = cv2.normalize(sobel, None, 0, 255, cv2.NORM_MINMAX)

        threshold = 50
        _, binary_image = cv2.threshold(sobel_normalized, threshold, 255, cv2.THRESH_BINARY)

        if binary_image.dtype != np.uint8:
            binary_image = (binary_image * 255).astype(np.uint8)

        # Finde alle Konturen in der binären Maske
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Berechne die Flächen der einzelnen Konturen
        areas = [cv2.contourArea(contour) for contour in contours if cv2.contourArea(contour) > 0]

        #cv2.drawContours(image, contours, -1, (0, 255, 0), 2)

        if not areas:
            return 0, image  # Keine weißen Flächen gefunden

        # Berechne die mittlere Fläche
        average_area = sum(areas) / len(areas)

        filtered_array = image[image != 0]
        min_value = np.min(filtered_array)
        max_value = np.max(filtered_array)
        return max_value - min_value, image

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

    def variance_of_laplacian_cuda(self, image):
        self.logger.info("Calculating Laplacian variance for picture quality")
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        image = np.uint8(image)
        image = Image.fromarray(image)

        transform = transforms.ToTensor()
        image_tensor = transform(image).unsqueeze(0).to(device)  # Unsqueeze fügt eine Batch-Dimension hinzu und das Tensor zur GPU senden
        laplacian_kernel = torch.tensor([[0, 1, 0],
                                        [1, -4, 1],
                                        [0, 1, 0]], dtype=torch.float32, device=device).unsqueeze(0).unsqueeze(0)

        # Anwenden des Laplace-Filters auf das Bild
        laplacian = F.conv2d(image_tensor, laplacian_kernel, padding=1)
        #transform = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor()])
        mean = torch.mean(image_tensor)
        variance = torch.mean((image_tensor - mean) ** 2)
        variance_float = variance.item()
        return variance_float, laplacian

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

    def _template_matching_for_scale(self, image, scale=1.05):
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

    def plotGraPh(self, positions, metrics, found, ax_big, fig, gs, counter):
        ax_big.clear()
        ax_big.plot(positions[:len(metrics)], metrics, 'o', label='Original data')
        #plt.subplot(1, 3, 3)
        #axs[1].imshow(found, cmap='gray')
        plt.pause(0.005)
        #plt.subplot(1, 2, 2)
        ax = fig.add_subplot(gs[1, counter])
        ax.imshow(found, cmap='gray')
        plt.tight_layout()
        plt.pause(0.005)

    def load_and_show_pic(self):
        root = tk.Tk()
        root.withdraw()  # Verstecke das Tk-Fenster

        # Dateiauswahldialog öffnen und ausgewählte Datei speichern
        file_path = filedialog.askopenfilename(title="Bild auswählen", filetypes=(("JPG Dateien", "*.jpg"), ("Alle Dateien", "*.*")))
        if file_path:
            bild = Image.open(file_path)
            plt.imshow(bild)
            plt.axis('off')  # zum Ausschalten der Achsenbeschriftungen
            plt.show()

    def move_light_in_center(self, experimet_name):
        self.galvo.applyVoltageToDAC0to1024("DAC0", self.pos_laser[0])
        self.galvo.applyVoltageToDAC0to1024("DAC1", self.pos_laser[1])

        self.Camera.take_picture(experimet_name)
        image_dir = f"C:/GithubSync/pictures taken/{experimet_name}"

        time.sleep(0.1)
        image_path = self.get_latest_image(image_dir)
        image = cv2.imread(image_path)
        image = image[:, :, 1]
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(image)
        max_position = max_loc
        json_path = 'C:\GithubSync\pylabnet\pylabnet\scripts\data.json'
        with open(json_path, 'r') as file:
            data = json.load(file)

        optimal_horizontal = data['horizontal']
        optimal_vertical = data['vertical']

        delta_horizontal = optimal_horizontal - max_position[0]
        delta_vertical = optimal_vertical - max_position[1]

        print(delta_horizontal, delta_vertical)

        self.pos_laser[1] = self.pos_laser[1] - int(delta_horizontal * 100 / 1222)
        self.pos_laser[0] = self.pos_laser[0] + int(delta_vertical * 100 / 1222)
        print("Move to position: ", self.pos_laser)
        print("Changes in x and y: ", delta_horizontal, delta_vertical)

    def move_structure_in_middle(self):

    def analyse_given_pictures_focus(self):
        root = tk.Tk()
        root.withdraw()
        file_paths = filedialog.askopenfilenames(title="Select images", filetypes=(("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")))
        num_images = len(file_paths)
        fig, axs = plt.subplots(num_images, 2, figsize=(18, 6 * num_images), gridspec_kw={'width_ratios': [8, 1]})
        figsobel, axsobel = plt.subplots(1, num_images, figsize=(18, 6 * num_images))
        figerg, axserg = plt.subplots(1, 1, figsize=(18, 18))
        #fig_images = plt.figure(figsize=(15, 5))
        #fig_histograms = plt.figure(figsize=(15, 5))
        #fig_additional = plt.figure(figsize=(10, 5))
        quality_list = []
        picture_list = []
        quality_list2 = []

        for idx, file_path in enumerate(tqdm(file_paths, desc="Verarbeitung", unit="%")):
            image = cv2.imread(file_path)
            #gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image = image[:, :, 1]    # Roten Kanal extrahieren
            #image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            found = self._template_matching_for_scale(image)
            #quality, sobel_normalized = self.picture_quality_sobel_Konstantin(image)

            quality, image = self.picture_quality_sobel_Konstantin2(found)
            quality_list.append(quality)
            #quality_list2.append(quality2)
            picture_list.append(image)

            axsobel[idx].imshow(image, cmap='gray')
            axsobel[idx].axis('off')
            axsobel[idx].set_title('Sobel Image')

            min_element = int(np.min(image))
            max_element = int(np.max(image))
            #plt.figure()
            #ax = fig.add_subplot(num_images, 2, 3*idx + 2)
            #plt.subplot(1, len(file_paths), idx + 1)
            axs[idx, 0].hist(image.flatten(), bins=255, align='left', edgecolor='black')
            axs[idx, 0].set_yscale('log')
            axs[idx, 0].set_xlabel('Pixel Value')
            axs[idx, 0].set_ylabel('Count')
            axs[idx, 0].set_title(f'Histogram of Image {idx+1}')
            axs[idx, 0].grid()
            axs[idx, 0].set_xlim(0, 255)
            #ax.set_yticks([])
            #ax.set_xticks([])
            #plt.show()

        quality_list = quality_list / np.max(quality_list)
        #quality_list2 =quality_list2/np.max(quality_list2)

        def gewichte_berechnen(quality_list, anzahl_niedrige_werte, hoehere_gewichtung):
            # Sortiere die Liste und finde die Schwellenwerte für die niedrigsten N Werte
            sortierte_indices = np.argsort(quality_list)
            niedrigste_indices = sortierte_indices[:anzahl_niedrige_werte]

            # Initialisiere alle Gewichte mit 1
            gewichte = np.ones_like(quality_list)

            # Setze die Gewichte der niedrigsten N Werte auf einen höheren Wert
            gewichte[niedrigste_indices] = hoehere_gewichtung

            return gewichte

        # Berechne die Gewichte
        anzahl_niedrige_werte = 3
        hoeher = 0.5
        #gewichte = gewichte_berechnen(quality_list2, anzahl_niedrige_werte, hoeher)

        #quality_listges = (quality_list +gewichte *  quality_list2) / (gewichte + 1)
        axserg.scatter(range(len(quality_list)), quality_list)
        #axserg.scatter(range(len(quality_list2)),quality_list2)
        axserg.set_xlabel('Normed focus position')
        axserg.set_ylabel('Quality (low good)')
        axserg.set_title('Quality of focus positions')
        #axs[-1,2].axis('off')

        metrics = quality_list
        positions = range(len(metrics))
        coefficients = np.polyfit(positions, metrics, 2)

        f = interp1d(positions, metrics, kind='quadratic', fill_value="interpolate")
        fine_positions = np.linspace(positions[0], positions[-1], num=10000)
        fine_metrics = f(fine_positions)

        quadratic_function = np.poly1d(coefficients)
        fine_metrics2 = quadratic_function(fine_positions)

        #ax_big.clear()
        #ax_big.plot(positions, metrics, 'o', label='Original data')
        axserg.plot(fine_positions, fine_metrics2, '-', label='Interpolated curve')

        plt.tight_layout()
        plt.show()

    def optimize_focus(self, experimet_name, initial_position=None, start=None, step=None, end=None, plot=False):
        time_hole_process = time.time()
        if initial_position is None:
            initial_position = self.EAF.EAFget_position()
        if start is None:
            start = initial_position - 5000
        if end is None:
            end = initial_position + 5000
        if step is None:
            step = 1000

        positions = np.arange(start, end, step)
        metrics = []
        summetrics = np.empty((0, 3))

        fig, axs = plt.subplots(3, 1, figsize=(25, 20))  # 2 Zeilen, 1 Spalte (erst mal)
        gs = fig.add_gridspec(3, len(positions), height_ratios=[4, 1, 1])
        ax_big = fig.add_subplot(gs[0, :])
        ax_big.set_xlabel('EAF Position')
        ax_big.set_ylabel('Picture Quality')
        ax_big.set_title('Focus Optimization')
        ax_big.set_xlim(start, end)

        def column_normalize(arr):
            col_sum = arr.sum(axis=0)
            return arr / col_sum

        counter = 0
        seven_former_posiion = None
        all_pictures = []
        goodpictures = []

        for position in positions:
            time_moving = time.time()
            self.EAF.EAFmove(position)

            self.logger.info(f"Moving EAF to position {position}")
            while self.EAF.EAFis_moving():
                time.sleep(0.1)

            time_end_moving = time.time()
            print(f"Time for moving EAF: {time_end_moving - time_moving}")

            time_logger = time.time()
            self.galvo.send_area_scan_0to1024(300, 100, self.pos_laser[0], self.pos_laser[1], times=5)
            self.logger.info("Taking picture with camera")
            self.Camera.take_picture(experimet_name)
            image_dir = f"C:/GithubSync/pictures taken/{experimet_name}"

            time_end_logger = time.time()
            print(f"Time for taking picture: {time_end_logger - time_logger}")

            start_time = time.time()
            time.sleep(0.1)
            time_getting_image = time.time()
            image_path = self.get_latest_image(image_dir)
            time_end_getting_image = time.time()
            print(f"Time for getting image: {time_end_getting_image - time_getting_image}")

            image = cv2.imread(image_path)
            image = image[:, :, 1]    # Roten Kanal extrahieren
            all_pictures.append(image)
            #image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            time_matching = time.time()
            found = self._template_matching_for_scale(image)
            time_end_matching = time.time()
            print(f"Time for template matching: {time_end_matching - time_matching}")

            time_lopcuda = time.time()
            quality, analysed_image = self.picture_quality_for_focus(image)
            time_endcuda = time.time()
            print(f"Time for one picture process with cuda: {time_endcuda - time_lopcuda}")
            #quality, analysed_image = self.picture_quality_Brisque(image)
            #quality3, analysed_image = self.picture_quality_sobel(found)

            ##new_row = np.array([quality1,quality2,quality3])
            #new_row = new_row.reshape(1, 3)
            #summetrics = np.append(summetrics, new_row, axis=0)
            metrics.append(quality)

            #if found is None:
            #    self.logger.warning(f"Template matching failed for position {position}")
            #    continue

            #quality, analysed_image = self.picture_quality_Brisque(found)

            time_plotting = time.time()

            if plot:
                # p = Process(target=plotGraph, args=(positions, metrics, found, ax_big, fig, gs, counter,))
                # p.start()
                # p.join()
                #plot_subprocess(positions, metrics, found, ax_big, fig, gs, counter)
                #a = subprocess.run(self.plotGraPh(positions, metrics, found, ax_big, fig, gs, counter),errors='ignore')
                #time.sleep(5)
                #plt.subplot(1, 2, 1)
                ax_big.clear()
                ax_big.set_xlabel('EAF Position')
                ax_big.set_ylabel('Picture Quality')
                ax_big.set_title('Focus Optimization')
                ax_big.set_xlim(start - (end - start) / 20, end + (end - start) / 20)
                ax_big.grid()
                ax_big.plot(positions[:len(metrics)], metrics, 'o', label='Original data')
                #plt.subplot(1, 3, 3)
                #axs[1].imshow(found, cmap='gray')
                plt.pause(0.005)
                #plt.subplot(1, 2, 2)
                ax = fig.add_subplot(gs[1, counter])
                ax.imshow(found, cmap='gray')

                ax2 = fig.add_subplot(gs[2, counter])
                ax2.imshow(analysed_image, cmap='gray')
                plt.tight_layout()
                plt.pause(0.005)

            time_endplotting = time.time()
            print(f"Time for plotting: {time_endplotting - time_plotting}")
            counter += 1
            end_time = time.time()
            print(f"Time for one picture process without taking picture: {end_time - start_time}")

        #normalized_metrics = column_normalize(summetrics)
        #summed_array = np.sum(normalized_metrics, axis=1)

        coefficients = np.polyfit(positions, metrics, 2)

        f = interp1d(positions, metrics, kind='quadratic', fill_value="interpolate")
        fine_positions = np.linspace(positions[0], positions[-1], num=10000)
        fine_metrics = f(fine_positions)

        quadratic_function = np.poly1d(coefficients)
        fine_metrics2 = quadratic_function(fine_positions)

        max_position = int(fine_positions[np.argmin(fine_metrics2)])

        #for now only this

        # if max_position <= positions[0] or max_position >= positions[-1]:
        #     self.logger.info("Optimized focus is at edge of search range. Need to redo")
        #     if max_position <= positions[0]:
        #         return self.optimize_focus(experimet_name, initial_position - 1000, plot = plot)
        #     if max_position >= positions[-1]:
        #         return self.optimize_focus(experimet_name, initial_position + 1000, plot = plot)
        #     # if initial_position + (end-start)/2 >= 30000 or initial_position - (end-start)/2 <= 0:
        #     self.logger.info("Optimized focus is at edge of search range. No further search possible.")
        #     return initial_position
        # range_adjustment = 5000 if max_position >= positions[-1] else -5000
        # return self.optimize_focus(experimet_name, initial_position + range_adjustment, plot = plot)

        index_min_value = metrics.index(max(metrics))
        max_position = positions[index_min_value]
        goodpictures = all_pictures[index_min_value]
        verzeichnis = f'C:/GithubSync/pictures taken/{experimet_name}/goodpics/'
        dateiname = f'C:/GithubSync/pictures taken/{experimet_name}/goodpics/' + datetime.now().strftime('%Y_%m_%d_%H_%M_%S') + '.jpg'
        verzeichnis = os.path.dirname(dateiname)
        if os.path.isdir(verzeichnis) == False:
            os.mkdir(verzeichnis)
        cv2.imwrite(dateiname, goodpictures)
        self.logger.info(f"Moving EAF to optimized position {max_position}")
        self.EAF.EAFmove(max_position)

        if plot:
            #plt.figure()
            ax_big.clear()
            ax_big.plot(positions, metrics, 'o', label='Original data')
            ax_big.plot(fine_positions, fine_metrics2, '-', label='Interpolated curve')
            #plt.plot(positions, summed_array, 'o', label='Summed data')
            #ax_big.xlabel('EAF Position')
            #ax_big.ylabel('Picture Quality')
            #ax_big.title('Focus Optimization')
            #ax_big.legend()
            plt.pause(0.05)
        #plt.show(block = True)
        time_end_process = time.time()
        print(f"Time for whole process: {time_end_process - time_hole_process}")
        self.logger.info(f"Optimized focus at position {max_position}")
        plt.close('all')

        return max_position


# Usage example:

if torch.cuda.is_available():
    print("CUDA is available. Using GPU:", torch.cuda.get_device_name(0))
else:
    print("CUDA is not available. Using CPU.")


if __name__ == "__main__":

    logger = lg.LogClient()
    galvo = hm.autoconnect_device(device_tag='Arduino_Galvo', logger=logger)
    ZWOCamera = hm.autoconnect_device(device_tag='ZWOCamera', logger=logger)
    nktLaser = hm.autoconnect_device(device_tag='white_laser', logger=logger)
    EAF = hm.autoconnect_device(device_tag='EAF_Telescope', logger=logger)

    nktLaser.emission_on()
    initial_position = 13000
    #EAF.EAFmove(initial_position)
    #while EAF.EAFis_moving():
    #    time.sleep(0.1)
    pos = EAF.EAFget_position()

    experiment_name = "Testingwithfocus"
    template_path = "C:/GithubSync/8.png"
    optimizer = FocusOptimizer(EAF, galvo, ZWOCamera, logger, nktLaser, template_path, pos_laser=[632, 602])
    optimizer.move_light_in_center(experiment_name)
    #optimizer.load_and_show_pic()
    #optimizer.optimize_focus(experiment_name,galvo, plot=True, start= pos-5000, step=1000, end=pos+5000)
   # optimizer.analyse_given_pictures_focus()
