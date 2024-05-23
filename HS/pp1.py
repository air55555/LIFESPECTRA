import numpy as np
import spectral
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import mplcursors

# Загрузка данных
img_filename = r"C:\PyProj\HSLidar\Datasets\ready\tuy.hdr"  # Имя файла с гиперспектральными данными ENVI
hdr_img = spectral.open_image(img_filename)
hyperspectral_image = hdr_img.load()

lidar_filename = r"C:\PyProj\HSLidar\Datasets\ready\readyfoo.csv"  # Имя файла с данными LiDAR в формате изображения
lidar_data = np.loadtxt(lidar_filename, delimiter=',')

# Преобразование данных LiDAR в трехмерное пространство
x, y = np.meshgrid(np.arange(0, 281, 5), np.arange(0, 128, 5))  # Используем срезы для уменьшения объема данных
z = lidar_data[::5, ::5]  # Используем срезы для уменьшения объема данных

# Нормализация координат
x_norm = (x / 280) * 1124
y_norm = (y / 127) * 1024

# Создание 3D графика облака точек
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
scatter = ax.scatter(x_norm.flatten(), y_norm.flatten(), z.flatten(), c=z.flatten(), cmap='jet', s=2)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D визуализация LiDAR данных')


# Функция для отображения спектра гиперспектрального изображения
def show_spectrum(sel):
    ind = sel.target.index
    x_idx = ind % 56
    y_idx = ind // 56
    print(f"Выбранный пиксель LiDAR: X={x_idx}, Y={y_idx}, Z={z[y_idx, x_idx]}")
    k = []

    # Выводим спектр для выбранного пикселя из гиперспектрального изображения
    spectrum = hyperspectral_image[y_idx, x_idx, :]
    for i in range(224):
        # print(spectrum[0,0,i])
        k.append(spectrum[0, 0, i])
    plt.figure()
    plt.plot(k)
    plt.title('Спектр для выбранного пикселя')
    plt.xlabel('Каналы спектра')
    plt.ylabel('Интенсивность')
    plt.show()


# Инициализация инструмента mplcursors
cursor = mplcursors.cursor(scatter, hover=True)
cursor.connect("add", show_spectrum)

plt.show()
