import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import spectral
# Загрузка данных
# Предположим, что у вас есть два массива данных: hyperspectral_image и lidar_data

# Гиперспектральное изображение
img_filename = r"C:\PyProj\HSLidar\Datasets\ready\tuy.hdr"  # Имя файла с гиперспектральными данными ENVI
hdr_img = spectral.open_image(img_filename)
hyperspectral_image = hdr_img.load()

# Загрузка данных LiDAR Ouster в виде 2D изображения
lidar_filename = r"C:\PyProj\HSLidar\Datasets\ready\readyfoo.csv"  # Имя файла с данными LiDAR в формате изображения
#lidar_img = plt.imread(lidar_filename)
lidar_data = np.loadtxt(r"C:\PyProj\HSLidar\Datasets\ready\readyfoo.csv", delimiter=',')
# 1. Преобразование данных Лидара в трехмерное пространство
# Создаем массив для трехмерных координат
x, y = np.meshgrid(np.arange(281), np.arange(128))  # Обратите внимание на изменение порядка
z = lidar_data

# 2. Совмещение с гиперспектральным изображением
x_norm = (x / 281) * 1124  # Нормализация x координат
y_norm = (y / 128) * 1024  # Нормализация y координат

# Функция для отображения спектра для выбранной точки
def plot_spectrum(event):
    if event.inaxes is None:
        return
    x, y = event.xdata, event.ydata
    print("x:", x, "y:", y)  # Выводим координаты x и y для отладки
    x_index = int((x / 1124) * 1123)  # Индекс по x
    y_index = int((y / 1024) * 1023)  # Индекс по y
    print("x_index:", x_index, "y_index:", y_index)  # Выводим индексы для отладки
    spectrum = hyperspectral_image[y_index, x_index, :]
    k = []
    for i in range(224):
        #print(spectrum[0,0,i])
        k.append(spectrum[0,0,i])
    print("Spectrum values:", spectrum[0,0,1])  # Выводим значения спектра для отладки
    plt.figure()
    plt.plot(k)
    plt.title('Спектр для выбранной точки')
    plt.xlabel('Каналы спектра')
    plt.ylabel('Интенсивность')
    plt.show()

# Создание фигуры
fig, ax = plt.subplots()
ax.imshow(lidar_data.T, cmap='gray', extent=[0, 1124, 0, 1024], origin='lower')  # Используем .T для транспонирования
ax.set_title('2D изображение Лидара')
ax.set_xlabel('X')
ax.set_ylabel('Y')
plt.colorbar(ax.imshow(lidar_data.T, cmap='viridis', extent=[0, 1124, 0, 1024], origin='lower'), ax=ax, label='Расстояние до объекта')

# Добавление обработчика событий для отображения спектра при щелчке на точке
fig.canvas.mpl_connect('button_press_event', plot_spectrum)

plt.show()