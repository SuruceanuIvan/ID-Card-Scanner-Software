# ID-Card-Scanner-Software

![stand_functional](https://github.com/user-attachments/assets/f6cc745d-cd59-48f8-842c-89c26c747f81)

<p>Worked in a team to develop an <b>ID card scanning system</b> designed to manage and secure access for dormitory visitors. My main responsibility was <b>software development</b>, focusing on automation, data extraction, and user interaction.</p>

<p>The system detected ID cards, extracted personal data using <b>Python and PyTesseract</b>, and automatically registered visitor and room information. It also provided <b>real-time feedback</b> through LEDs and a graphical interface, improving usability.</p>

<p>Hardware components included a <b>Raspberry Pi, distance sensor, servomotor, and LED indicators</b>, all integrated through custom control scripts. The software was developed using <b>object-oriented programming (OOP)</b> principles and featured a <b>database</b> for storing visitor records and access logs.</p>

<p>The result was a <b>fully functional system</b> that simplified visitor registration, improved security, and enhanced the efficiency of dorm access management. Through this project, I gained significant experience in <b>automation, image processing,</b> and <b>hardware–software integration.</b></p>

## Hardware Schematic Reference

<img width="1364" height="618" alt="electronic_schematic" src="https://github.com/user-attachments/assets/f6b3843e-b0e3-42d4-b80d-909559c401fa" />

The electronic schematic illustrates the <b>main hardware</b> components used in the ID Card Scanner System. While my contribution focused on <b>software development</b>, the following hardware elements form the physical foundation of the project:

<ul>
<li><b>12V 10A Power Supply</b> – provides stable electrical power for the system.</li>

<li><b>2× DC-DC Converter 5–32V to 1.25–32V 4.5A Step-Down (CV Mode)</b> – used to regulate and adapt voltage levels for different components.</li>

<li><b>Adjustable Buck Converter Module with Display (LM2596, 4–40V)</b> – allows precise control of output voltage, with visual feedback.</li>

<li><b>1-Channel Relay Module, 3.3V, Low-Level Trigger</b> – enables controlled switching of high-power circuits through the Raspberry Pi.</li>

<li><b>MG996 Digital Metal Servo Motor (90°)</b> – provides mechanical movement for scanning or access mechanisms.</li>

<li><b>COB LED Module, Warm White, Matte Cover, 12V DC, 1.8W, IP67</b> – used for illumination of the scanning area.</li>

<li><b>Control Lamp, Blue LED 12V, 5mm</b> – status indicator for power or system activity.</li>

<li><b>Momentary Push Button Switch (No Latch)</b> – user input for system control.</li>

<li><b>RFID Module RC522</b> – used for reading ID cards and authentication.</li>

<li><b>Cooling Fan 12V, 40×40×10mm (CY410/A)</b> – ensures proper ventilation and temperature control.</li>

<li><b>Pololu Carrier with Sharp GP2Y0D805Z0F Digital Distance Sensor (5 cm)</b> – detects object presence or distance for precise operation.</li>

<li><b>Raspberry Pi 5</b> – main processing unit for software control and data handling.</li>

<li><b>Raspberry Pi Touch Display 2</b> – interactive interface for the user.</li>

<li>2<b>× Electrical Junction Box 253×250×70 mm (IP56, no gasket)</b> – protective enclosures for the electronic components.</li>

<li><b>Joyusing V500SUSB Document Camera</b> – used for capturing and processing ID card images</li>
</ul>

![scanner_close_up](https://github.com/user-attachments/assets/b64ee909-cca5-412e-a6cd-952409bc7b96)

## Code Overview
## Data Base Structure

<img width="600" height="392" alt="baza_de_date" src="https://github.com/user-attachments/assets/f408ec77-5c30-4f15-bfd5-a377b248ce93" />

The database designed for the ID Card Scanner System includes three main tables:
<ul>
<li><b>vizitator (<i>visitor</i>)</b> – stores personal information about each visitor, including their first name, last name, ID card series and number, and a field for storing the visitor’s facial image (this feature was not implemented in the final version due to time constraints). </li>

<li><b>vizitator_card (<i>visitor_card</i>)</b> – manages the association between each visitor and a unique guest card that contains an RFID identification number. The card must be scanned by the RFID reader to verify the visitor’s identity.</li>

<li><b>vizitator_timp (<i>visitor_time</i>)</b> – records the room number and the time of entry and exit for each visitor, enabling tracking of visit history within the system.</li>
</ul>
Table relationships:
<ul>
<li>The relationship between vizitator and vizitator_card is <b>one-to-one</b>, since each visitor is assigned a single guest card.</li>

<li>The relationship between vizitator and vizitator_timp is <b>one-to-many</b>, allowing multiple time entries to be stored for a single visitor (for example, multiple visits).</li>
</ul>

## Object-Oriented Design

<img width="892" height="738" alt="uml_oop" src="https://github.com/user-attachments/assets/b2653b76-3721-4f9d-938a-4fb13ba90c95" />

To make the codebase easier to understand, maintain, and extend, I applied Object-Oriented Programming (OOP) principles.
The system is structured around five main classes:

<ul>
<li><p><b>Guest</b> – represents the Guest table from the database.</p>
<p>This class serves as a data model and <i>does not implement SQL operations directly</i> due to its abstraction level.</p>
<p>It has an <b>aggregation relationship</b> with the DBHandler class.</p></li>

<li><p><b>DBHandler</b> – <i>responsible for executing SQL queries</i> and managing all interactions with the database.</p>
<p>It operates independently of Guest, but can process and update data from it when needed.</p>
<p>The class <b>inherits</b> from DateTime to simplify time and date handling across the system.</p></li>

<li><p><b>DateTime</b> – provides methods for <b>extracting, formatting,</b> and <b>manipulating time</b> and date values used by other classes.</p>
<p>Its purpose is to <i>centralize time-related functionality</i> to ensure code consistency.</p></li>

<li><p><b>Imagine (Image)</b> – represents an <b>image captured from the camera</b>, storing the path to the file on the local device.</p>
<p>This class <i>encapsulates basic image-related data and metadata.</i></p></li>

<li><p><b>ImagineTools (ImageTools)</b> – extends the Imagine class to add <b>image processing</b> functionality.</p>
<p>It is used to <i>analyze ID card images</i> and extract the necessary data for identification or database entry.</p></li>
</ul>

This class structure provides a clear separation of responsibilities and improves code modularity.

## Code 
### Imagine Class
```python
class Imagine:
    def __init__(self, calea):
        '''
          _calea – stores the file path of the image on the local device.
          It is prefixed with an underscore to indicate it is intended as a protected member.
        '''
        self._calea = calea
    
    def getCalea(self):
        '''
          – returns the stored image path. This allows other classes or functions
          to retrieve the image location without directly accessing the internal attribute.
        '''
        return self._calea

    def getCV2Image(self):
        '''
          – uses OpenCV (cv2) to read the image from the stored path and return it as a NumPy array,
          which can then be processed for tasks such as ID card analysis.
        '''
        return cv2.imread(self.getCalea())
```

The Imagine class provides a <b>centralized representation of images</b>, encapsulating the file path and providing an easy interface for retrieving the image in a format compatible with image processing libraries.
It serves as the <b>base class for ImagineTools</b>, which extends its functionality to analyze ID card images and extract required data.

<hr />

### ImagineTools class
```python
class ImagineTools:
    def __init__(self, imagine):
        '''
          _imagine – stores the image (as a NumPy array) that the class will process.
          It can be an image loaded via Imagine.getCV2Image() or already processed.
        '''
        self._imagine = imagine
    
    def blackAndWhite(self):
        '''
          – converts the image to grayscale and then applies binary thresholding,
          producing a black-and-white version suitable for OCR (text extraction).
        '''
        grayImage = cv2.cvtColor(self.getImagine(), cv2.COLOR_BGR2GRAY)

        (thresh, self._imagine) = cv2.threshold(grayImage, 127, 255, cv2.THRESH_BINARY)

    def getSeriaNumar(self):
        '''
          – extracts the ID card series and number from a predefined area on the card image using Tesseract OCR.
          Returns a tuple (series, number).
        '''
        buletin_stanga_jos = self.getImagine()[370:404, 36:166]

        text_stanga_jos = pytesseract.image_to_string(buletin_stanga_jos, lang="ron", config=Const.MYCONFIG)

        return (text_stanga_jos[0:2], text_stanga_jos[2:-1])

    def getNames(self):
        '''
           – extracts the first name(s) and last name from the ID card by analyzing a specific region of the image.
          Performs text cleaning by splitting on < characters and filtering empty strings.
          Returns a tuple with the extracted names.
        '''
        buletin_jos_sus = self.getImagine()[330:369, 40:590]

        text_jos_sus = pytesseract.image_to_string(buletin_jos_sus, lang="ron", config=Const.MYCONFIG)

        lista_text_jos_sus = text_jos_sus.split("<")
        lista_text_jos_sus.pop()
        lista_text_jos_sus[0] = lista_text_jos_sus[0][5:]

        lista_buna = list()

        for i in range(len(lista_text_jos_sus)):
            if lista_text_jos_sus[i] != "" and lista_text_jos_sus[i] != " ":
                lista_buna.append(lista_text_jos_sus[i])

        return tuple(lista_buna)

    def getImagine(self):
        '''
          – returns the current state of the image stored in _imagine
        '''
        return self._imagine
```
<b>ImagineTools</b> provides a specialized toolset for ID card image processing.
It extends the base Imagine class and allows the system to <b>automatically extract</b> critical data from ID cards, such as the visitor’s name and ID number, facilitating database entry and verification.

<hr />

### Guest class
```python
class Guest:
    def __init__(self, nume, prenume, seria, numar, id=0, poza=""):
        ```
          _nume – visitor’s last name

          _prenume – visitor’s first name

          _seria – ID card series

          _numar – ID card number

          _id – unique identifier in the database (optional, default 0)

          _poza – path to the visitor’s facial image (optional, default empty string)
        ```
        self._nume = nume
        self._prenume = prenume
        self._seria = seria
        self._numar = numar
        self._id = id
        self._poza = poza

    def getProps(self):
        '''
          – returns all visitor properties as a tuple, useful for database insertion or display.
        '''
        return (self.getID(), self.getNume(), self.getPrenume(), self.getSeria(), self.getNumar(), self.getPoza())

    def getNume(self):
        return self._nume
    
    def getPrenume(self):
        return self._prenume
    
    def getSeria(self):
        return self._seria
    
    def getNumar(self):
        return self._numar
    
    def getID(self):
        return self._id
    
    def getPoza(self):
        return self._poza
```

The <b>Guest class</b> encapsulates the <b>visitor’s information</b> in a structured object-oriented way, enabling clean interaction with the database through DBHandler and integration with other components such as image processing (Imagine / ImagineTools).

It <b>does not handle SQL queries itself</b>, maintaining a clear separation between data representation and database operations.

<hr />

### DateTime class

```python
class DateTime:
    def __init__(self, template = "%d/%m/%Y %H:%M:%S"):
        '''
          _template – stores the string template used for formatting dates and times.
          The default format is "dd/mm/yyyy HH:MM:SS"
        '''
        self._template = template

    def getStamp(self):  
        '''
          – returns the current date and time as a formatted string according to the template defined in _template.
          Uses Python’s datetime.now() and strftime() for formatting.
        '''
        now = datetime.now()

        dt_string = now.strftime(self.getTemplate())
        
        return dt_string
    
    def getTemplate(self):
        '''
          – returns the current date-time format template.
        '''
        return self._template
```

The <b>DateTime</b> class is inherited by other classes, such as DBHandler, to provide consistent timestamp generation across different system operations. This ensures that database records, logs, and other time-dependent functions are synchronized and formatted uniformly.

<hr />

### DBHandler

```python
class DBHandler:
    DB_NAME = "project.db"

    def __init__(self):
        '''
            – establishes a connection to the SQLite database (project.db)
            and initializes a cursor for executing SQL queries.
        '''
        self._con = sql3.connect(DBHandler.DB_NAME)

        self._cursor = self.getConnection().cursor()

    def verifyExistentGuest(self, serie_numar):
        '''
            – checks whether a guest with a specific ID card series and number exists in the vizitator table.
            Returns the guest ID if found, otherwise returns False
        '''
        ver = self.getCursor().execute(f"SELECT * FROM vizitator WHERE seria='{serie_numar[0]}' AND numar='{serie_numar[1]}'")

        rezultat = ver.fetchall()

        if len(list(rezultat)):
            return list(rezultat)[0][0]
        else:
            return False
    
    def scanGuest(self, guest : Guest):
        '''
            – adds a new guest to the database if they do not already exist.
            Returns a Guest object updated with the database ID.
        '''
        guest_data = guest.getProps()

        if self.verifyExistentGuest((guest_data[3], guest_data[4])) == False:
            self.getCursor().execute("INSERT INTO vizitator (nume, prenume, seria, numar, poza) VALUES(?, ?, ?, ?, ?)", guest_data[1:])

            self.getConnection().commit()

            guest = Guest(*guest_data[1:-1], self.verifyExistentGuest((guest_data[3], guest_data[4])), guest_data[-1])
        else:
            guest = Guest(*guest_data[1:-1], self.verifyExistentGuest((guest_data[3], guest_data[4])), guest_data[-1])

        return guest
    
    def giveCard(self, guest, code, nr_camera):
        '''
            – logs the assignment of a unique guest card (RFID) and records the room number and entry time in the database.
        '''
        data_time = DateTime()

        timp = data_time.getStamp()

        self.getCursor().execute("INSERT INTO vizitator_timp (vizitator_id, numar_camerei, time_in) VALUES(?, ?, ?)", (guest.getID(), nr_camera, timp))
        self.getConnection().commit()

        self.getCursor().execute("INSERT INTO vizitator_card (vizitator_id, card_key, time_in) VALUES(?, ?, ?)", (guest.getID(), code, timp))
        self.getConnection().commit()
    
    def takeCard(self, code):
        '''
            – logs the exit time for a guest when the card is returned and deletes the corresponding entry in vizitator_card.
        '''
        data_time = DateTime()

        self.getCursor().execute(f"""UPDATE vizitator_timp
                SET time_out = '{data_time.getStamp()}'
                WHERE vizitator_id = (
                    SELECT vizitator_id FROM vizitator_card
                    WHERE card_key = '{code}'
                    ORDER BY time_in DESC
                    LIMIT 1
                ) AND time_in=(SELECT time_in FROM vizitator_card WHERE card_key='{code}' ORDER BY time_in DESC LIMIT 1)""")
        self.getConnection().commit()

        self.getCursor().execute(f"DELETE FROM vizitator_card WHERE card_key='{code}'")
        self.getConnection().commit()

    def getConnection(self):
        return self._con
    
    def getCursor(self):
        return self._cursor

```

The <b>DBHandler class</b> implements the <b>data access layer</b>, handling all interactions between the application and the database.

It <b>aggregates</b> Guest objects to manipulate their data in the database.

It <b>inherits</b> DateTime functionality indirectly by creating DateTime objects to log entry and exit times consistently.

The class ensures that database operations are <b>encapsulated</b>, making the system more maintainable and reducing the risk of SQL-related errors.

<hr />

### start_live_feed()

```python
def start_live_feed():
    global w
    
    cap = cv2.VideoCapture(0)  # Open default camera

    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    window = tk.Toplevel(w)
    window.title("Feed Live de la Cameră")

    window_width = 750
    window_height = 550
    canvas = tk.Canvas(window, width=window_width, height=window_height)
    canvas.pack()

    def update_frame():
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_pil = Image.fromarray(frame_rgb)
            image_resized = image_pil.resize((window_width, window_height))
            imgtk = ImageTk.PhotoImage(image=image_resized)
            canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            canvas.imgtk = imgtk
        
        sensor.when_pressed = led.off
        window.after(10, update_frame)

    update_frame()

    capture_button = tk.Button(
        window,
        text="Capturează Imagine",
        command=lambda: capture_image_and_close(window, cap),
        width=120,
        height=100,
        background="green"
    )
    capture_button.pack()

    window.mainloop()
```

<b>Description of Functionality:</b>

<ul>
<li><b>Camera Initialization:</b></li>

<ul><li>Opens the default camera (cv2.VideoCapture(0)) and sets the resolution to 1920×1080.</li></ul>

<li><b>Tkinter Window Setup:</b></li>

<ul><li>Creates a separate Toplevel window.</li>

<li>A Canvas is used to display the live video feed.</li></ul>

<li><b>Live Feed Update (update_frame):</b></li>

<ul><li>Reads frames from the camera.</li>

<li>Converts the image from BGR (OpenCV format) to RGB.</li>

<li>Resizes the frame to fit the window dimensions.</li>

<li>Displays the frame in the Tkinter canvas.</li>

<li>Updates the feed every 10 milliseconds using window.after().</li></ul>

<li><b>Capture Button</b>:</li>

<ul><li>Adds a button to capture the current frame and close the feed.</li>

<li>Calls capture_image_and_close(window, cap) when clicked.</li></ul>

<li><b>GPIO Integration:</b></li>

<ul><li>Example line sensor.when_pressed = led.off shows interaction with external hardware (like a sensor or LED), demonstrating that the GUI can integrate with physical components.</li></ul>

</ul>

This function provides a <b>user-friendly interface</b> for live camera monitoring and image capture, forming the basis for ID card scanning.
It <b>bridges the hardware</b> (camera and sensors) and the software processing modules (Imagine / ImagineTools) by supplying image data for further analysis.

<hr />

### capture_

```python
def capture_image_and_close(window, cap):
    global nr_camerei

    image_path = f"buletin_{strftime('%Y%m%d_%H%M%S')}.jpg"
    
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(image_path, frame)
        messagebox.showinfo("Imagine Capturată", f"Imaginea a fost salvată!\nLuați un card și plasati-l pe cititorul de card.")
    
    nr_card = card.obtainUID()

    img = bck.Imagine("buletin_scanat.jpg")
    img_tools = bck.ImagineTools(img.getCV2Image())
    img_tools.blackAndWhite()

    guest = bck.Guest(
        img_tools.getNames()[0],
        "-".join(img_tools.getNames()[1:]),
        img_tools.getSeriaNumar()[0],
        img_tools.getSeriaNumar()[1],
        0,
        "buletin_scanat.jpg"
    )
    print(guest.getProps())

    vizitator = guest
    card_cheie = nr_card

    # Database operations (commented out in this snippet)
    # db = bck.DBHandler()
    # guest = db.scanGuest(guest)
    # db.giveCard(guest, nr_card, nr_camerei)

    messagebox.showinfo("Card Info", f"Cardul cu nr. {nr_card} a fost asociat cu succes!.")

    cap.release()
    window.destroy()

    afiseaza_date_vizitator(guest)
```

<b>Description of Functionality:</b>

<ul>
<li>Capture and Save Image:</li>

<ul><li>Reads a frame from the camera feed.</li>

<li>Saves the image with a timestamp-based filename for traceability.</li>

<li>Notifies the user that the image has been saved.</li></ul>

<li>Read RFID Card:</li>

<ul><li>Retrieves the unique card ID from the card reader.</li></ul>

<li>Process Captured Image:</li>

<ul><li>Initializes the Imagine and ImagineTools classes to process the image.</li>

<li>Converts the image to black-and-white for better OCR results.</li>

<li>Extracts visitor names and ID card series/number.</li></ul>

<li>Create Guest Object:</li>

<ul><li>Constructs a Guest object with the extracted information.</li>

<li>Prints guest properties for verification.</li></ul>

<li>Database Interaction (Optional / Commented Out):</li>

<ul><li>Example code shows how the guest and card could be stored in the database using DBHandler.</li></ul>

<li>User Feedback:</li>

<ul><li>Displays confirmation messages for image capture and card association.</li></ul>

<li>Cleanup:</li>

<ul><li>Releases the camera resource.</li>

<li>Closes the Tkinter window.</li>

<li>Calls afiseaza_date_vizitator(guest) to display visitor data.</li><ul>
</ul>

This function ties together live <b>camera capture, image processing, visitor data extraction, and RFID card handling.</b>
It demonstrates the integration of GUI, hardware, and software modules to form a complete visitor identification workflow.

<hr />

# Thanks!
