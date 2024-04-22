import PySimpleGUI as sg


def create_gen(expos: int, frames: int, name: str, specim, FPS):
    return specim.capturing(expos, frames, name, FPS) if frames else specim.calibration(expos, FPS)


def create_predefined_frame(width, height, text="sample", color=(255, 255, 255), font_scale=1.0, thickness=2):
    """
    Creates a predefined frame with text on it.

    Args:
        width: Width of the frame in pixels.
        height: Height of the frame in pixels.
        text: Text to display on the frame (default: "sample").
        color: Color of the text (default: white (255, 255, 255)).
        font_scale: Font size scaling factor (default: 1.0).
        thickness: Thickness of the text in pixels (default: 2).

    Returns:
        A NumPy array representing the predefined frame with text.
    """

    # Create a black (BGR) frame of the specified size.
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame.fill(0)  # Fill with black color

    # Get text size using the specified font.
    text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)

    # Calculate text placement coordinates.
    text_x = int((width - text_size[0]) / 2)
    text_y = int((height + text_size[1]) / 2)

    # Add the text to the frame.
    cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

    return frame


BTN_COLOR = ('white', '#0D7377')
BGRND_COLOR = '#4D3E3E'
MINI_FONT = 'Helvetica 10 bold italic'
BIG_FONT = 'Helvetica 12 bold italic'

videostream_windows = [
    [sg.Image(size=(1024, 100), k='-WATERFALL'),
     sg.VerticalSeparator(), sg.Image(size=(600, 100), k='-SONY')]
]
videostream = [
    [sg.Frame('', videostream_windows, font=BIG_FONT, title_location=sg.TITLE_LOCATION_TOP)],
]
layout = [
    [sg.Frame('VideoStream', videostream, font=BIG_FONT, title_location=sg.TITLE_LOCATION_TOP)]
]
sg.theme('DarkBlack')
