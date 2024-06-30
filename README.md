
# Prayer Times Application

![](demo.gif)

This application displays prayer times and plays the adhan (call to prayer) at the appropriate times.

## Initial Setup

1. Clone the repository:

  ```
 git clone https://github.com/MohamedAli2310/PrayerTimes.git
```

> If this fails for macOS, you'll need to install Xcode command line interface. Run `xcode-select --install`

2. Make sure you have Python and pip installed:
   - Check Python version: `python --version` or `python3 --version`
   - Check pip version: `pip --version` or `pip3 --version`

   If not installed, download and install Python from [python.org](https://www.python.org/downloads/)

3. Navigate to the project directory:

   ``` cd PrayerTimes ```

4. Create a virtual environment (optional but recommended):

  ```
 python -m venv venv
```

5. Activate the virtual environment:
   - On Windows:

     ``` venv\Scripts\activate
```

   - On macOS and Linux:

     ```
source venv/bin/activate
```

> Note: you can use condo or any other virtual environment manager of your choice.

6. Install required packages:

  ```  pip install -r requirements.txt ```

## Additional Resources

7. The following files are included in the repository, but can be changed as needed:
   - `adhan.mp3`: An audio file for the call to prayer
   - `audio_icon.png`: An icon for the audio controls
   - `gear_icon.png`: An icon for the settings button

## Running the Application

8. Run the application:

   ``` python prayer_times.py ```

## Usage

- The application will display the current time, date, and prayer times for your location.
- Toggle buttons next to each prayer time allow you to enable/disable the adhan for that prayer.
- The audio icon will appear when the adhan is playing, and you can click it to stop the adhan.
- Use the gear icon to change the background color.
- The Dhuhr prayer time can be manually adjusted for testing purposes.

## Troubleshooting

- If you encounter any issues with playing the adhan, ensure that you have the necessary audio codecs installed on your system.
- For location-related issues, check your internet connection as the app uses an online API to determine your location.

## Customization

- You can replace the `adhan.mp3` file with your preferred adhan audio.
- Modify the `audio_icon.png` and `gear_icon.png` files to change the appearance of these buttons.
- Change application background color using the gear icon

## Exiting the Application

- Use the "Exit" button in the bottom-right corner to close the application.

## Contributing

Feel free to fork this repository and submit pull requests for any enhancements or bug fixes.
