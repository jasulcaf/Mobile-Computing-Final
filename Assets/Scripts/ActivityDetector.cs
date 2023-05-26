using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using System;
using System.IO;
using System.Text;
using System.Diagnostics;
using System.ComponentModel;
using System.Reflection;
using System.Threading;
using UnityEngine;

public class ActivityDetector : MonoBehaviour
{
    public Material wallColor;

    public AudioSource alarm;
    public AudioClip clip;
    public GameObject Activity_Sign;
    public GameObject Infos;

    // Global Vars
    // Light vars
    private readonly double LIGHT_OFF_THRESHOLD = .05;
    private readonly double LIGHT_ON_THRESHOLD = .75;
    private readonly double LIGHT_OFF_DECAY = .975;
    private readonly double LIGHT_ON_GROWTH = 1.25;
    // recording vars
    private readonly int WINDOW_LENGTH = 4; // 6 seconds of data
    private readonly int WINDOW_SLIDE = 1; // call model every 3 seconds
    private bool readyToDetect = false;
    private float timeRemaining = 0;
    private bool timerActive = false;
    private float timeRemainingJR = 0;
    private bool timerActiveJR = false;
    // other
    private string CURRDIRPATH = "";
    private string EXEFILE_PATH = "";
    private float currRGB = 0;
    List<string> detected_list = new List<string>();
    private string temp123= "";

    OculusSensorReader sensorReader;
    
    int framesReceived = 0;
    int secTracker = 0;
    string prevActivity = "---";
    readonly int NUM_HZ = 72;
    List<Dictionary<string, Vector3>> attributes_list = new List<Dictionary<string, Vector3>>();
    private bool isSleeping = false;

    // Mutexes... or is it Mutices?
    private static Mutex mut_CSV_PROC = new Mutex(); // for the csv file
    private static Mutex mut_DET_ACT = new Mutex(); // for the detected_activity var
    private static Mutex mut_ATTR_LIST = new Mutex(); // for the attributes list

    // this is the multithreading component so that there is no major frame 
    // spike when running the ML model.
    // Also going to include the CSV creation in this function for mutex
    // simplicity so that we dont have to pass over the mutex to this thread :)
    private void ThreadProc()
    {
        UnityEngine.Debug.Log("We in the new thread now.");
        // We are ready to analyze the previous 3 seconds of data
        // write to csv so the python file can reference it
        // gotta protect this with mutex m8
        UnityEngine.Debug.Log("About to enter mutex");
        mut_CSV_PROC.WaitOne();
        mut_ATTR_LIST.WaitOne();
        UnityEngine.Debug.Log("Entered mutex");
        // string path =  Path.Combine(Application.persistentDataPath, "curr_data.csv"); // FOR VR HEADSET
        string path = CURRDIRPATH + "/Assets/Resources/curr_data_FAKE.csv"; // FOR PC
        // Delete the file if exists
        if (File.Exists(path))
        {
            File.Delete(path);
        }

        string[] dimensions = {".x", ".y", ".z"};
        // Now create the csv file manually
        UnityEngine.Debug.Log("Writing to CSV");
        try{
            StreamWriter writer = new StreamWriter(path);  
            bool first_iter = true;
            int i = 0;
            foreach (var attributez in attributes_list)
            {
                if (first_iter)
                {
                    first_iter = false;
                    foreach (KeyValuePair<string, Vector3> feature in attributez)
                    {
                        foreach (string dimension in dimensions)
                        {
                            writer.Write(feature.Key + dimension);
                            writer.Write(",");
                        }
                    }
                    writer.Write("\n");
                }
                foreach (KeyValuePair<string, Vector3> feature in attributez)
                {
                    Vector3 vec = feature.Value;
                    writer.Write(vec.x);
                    writer.Write(",");
                    writer.Write(vec.y);
                    writer.Write(",");
                    writer.Write(vec.z);
                    writer.Write(",");
                }
                writer.Write("\n");
                // because of multithreading, its possible that attributes_list 
                // has data from FUTURE frames. We want to EXCLUDE this
                // data in our analysis. So we just take the first WINDOW_LENGTH
                // seconds of data 
                i++;
                if (i > NUM_HZ * WINDOW_LENGTH)
                {
                    break;
                }
            }
            writer.Close();
        }
        catch (Exception e)
        {
            UnityEngine.Debug.Log("Failure in csv file writing");
            // temp123 = e.Message;
            prevActivity = "Failure in csv file writing: " + e.Message;
            // release mut bruh
            mut_CSV_PROC.ReleaseMutex();
            mut_ATTR_LIST.ReleaseMutex();
            mut_DET_ACT.WaitOne();
            // Activity_Sign.GetComponent<TextMesh>().text = e.Message; ==> CANT DO THIS BC UNITY BAD
            mut_DET_ACT.ReleaseMutex();
            
            return;
            // return e.Message;
        }
        UnityEngine.Debug.Log("Done writing to csv");
        // we just saved the data. lets empty out the attributes list
        attributes_list.RemoveRange(0, Math.Max(WINDOW_SLIDE * NUM_HZ, attributes_list.Count));
        mut_ATTR_LIST.ReleaseMutex();
        // Call the python script xD
        string detected_activity = "";
        try{
            UnityEngine.Debug.Log("Starting python process!!");
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = EXEFILE_PATH; 
            start.UseShellExecute = false;
            start.RedirectStandardOutput = true;
            using(Process process = Process.Start(start))
            {
                UnityEngine.Debug.Log("Started python process. Waiting for output!");
                using(StreamReader reader = process.StandardOutput)
                {
                    detected_activity = reader.ReadToEnd();
                } 
            }
        }
        catch (Exception e)
        {
            UnityEngine.Debug.Log("Failure in python process");
            prevActivity = "Failure in python process: " + e.Message;
            // release mut bruh
            mut_CSV_PROC.ReleaseMutex();
            mut_DET_ACT.WaitOne();
            // Activity_Sign.GetComponent<TextMesh>().text = e.Message; ==> CANT DO THIS BC UNITY BAD
            mut_DET_ACT.ReleaseMutex();
            return;
        }
        // good to release this mut m8]
        // mut_CSV_PROC.ReleaseMutex();
        // UnityEngine.Debug.Log("Detected Activity:");
        // UnityEngine.Debug.Log(detected_activity);

        // // We've got some cleaning up to do 
        // // mutex to protect this stuff
        // mut_DET_ACT.WaitOne();
        // prevActivity = detected_activity;
        // detected_list.Add(detected_activity);
        // Activity_Sign.GetComponent<TextMesh>().text = detected_activity; ==> CANT DO THIS BC UNITY BAD

        // done w mutex
        mut_DET_ACT.ReleaseMutex();
    }
    void GetCurrentActivity(Dictionary<string, Vector3> attributes)
    {
        
        if (!readyToDetect)
        {
            if (attributes_list.Count > 0)
            {
                mut_ATTR_LIST.WaitOne();
                attributes_list.Clear();
                mut_ATTR_LIST.ReleaseMutex();
            }
            mut_DET_ACT.WaitOne();
            Activity_Sign.GetComponent<TextMesh>().text = "---";
            mut_DET_ACT.ReleaseMutex();
            return;
            // return "---";
        }
        // Store in attributes_list regardless of what we are about to do
        mut_ATTR_LIST.WaitOne();
        attributes_list.Add(attributes);
        mut_ATTR_LIST.ReleaseMutex();
        // UnityEngine.Debug.Log("this0");
        if (framesReceived < NUM_HZ * WINDOW_LENGTH) // first N seconds of data
        {
            // Not ready to do our analysis. Return Unknown ("---")
            framesReceived++;
            secTracker++;
            mut_DET_ACT.WaitOne();
            Activity_Sign.GetComponent<TextMesh>().text = "---";
            mut_DET_ACT.ReleaseMutex();
            return;
            // return "---";
        }
        if (secTracker < (NUM_HZ * WINDOW_SLIDE)) // Already did an analysis within the N sec
        {
            framesReceived++;
            secTracker++;
            mut_DET_ACT.WaitOne();
            Activity_Sign.GetComponent<TextMesh>().text = prevActivity;
            mut_DET_ACT.ReleaseMutex();
            return;
            // return prevActivity;
        }
        UnityEngine.Debug.Log("GetCurrentActivity");
        // Set these vars now so we dont have overlaps
        secTracker = 0;
        framesReceived ++;

        // START NEW THREAD! 
        UnityEngine.Debug.Log("Starting new thread!");
        Thread newThread = new Thread(new ThreadStart(ThreadProc));
        newThread.Start();
    }
    // Start is called before the first frame update
    void Start()
    {
        sensorReader = new OculusSensorReader();
        // CURRDIRPATH = Application.persistentDataPath; // FOR VR HEADSET
        CURRDIRPATH = Directory.GetCurrentDirectory(); // FOR PC ==> this is the path to the /Mobile-Computing-Final folder :)
        UnityEngine.Debug.Log("CURRDIRPATH:");
        UnityEngine.Debug.Log(CURRDIRPATH);
        // PARENTDIRPATH = Directory.GetParent(CURRDIRPATH).ToString();
        // UnityEngine.Debug.Log("PARENTDIRPATH:");
        // UnityEngine.Debug.Log(PARENTDIRPATH);
        // EXEFILE_PATH = Path.Combine(CURRDIRPATH, "dist/predict_continuous/predict_continuous"); // FOR VR 
        EXEFILE_PATH = CURRDIRPATH + "Python/predict_continuous.py"; // FOR PC
        UnityEngine.Debug.Log("EXEFILE_PATH:");
        UnityEngine.Debug.Log(EXEFILE_PATH);

        Color CurrColor = wallColor.GetColor("_Color");
        currRGB = CurrColor.r;
    }
    // void StartSleeping(Color CurrColor
    // {
    //     wallColor
    // }
    // void StopSleeping(Color CurrColor)
    // {
        
    // }
    // Update is called once per frame
    void updateWallColor()
    {
        float newRGB = 0;
        float newTextRGB = 0;
        bool updateNeeded = false;
        if(isSleeping && currRGB > 0)
        {
            // Turn lights off gradually
            if(currRGB < LIGHT_OFF_THRESHOLD)
            {
                newRGB = 0;
                newTextRGB = 1;
            }
            else
            {
                newRGB = currRGB * ((float) LIGHT_OFF_DECAY);
                newTextRGB = (float) LIGHT_ON_THRESHOLD - newRGB;
            }
            updateNeeded = true;
        }
        else if(!isSleeping && currRGB < LIGHT_ON_THRESHOLD)
        {
            // Turn lights on gradually

            newRGB = (float) Math.Min(LIGHT_ON_THRESHOLD, (float) (Math.Max(LIGHT_OFF_THRESHOLD, currRGB)) * LIGHT_ON_GROWTH);
            newTextRGB = (float) LIGHT_ON_THRESHOLD - newRGB;
            updateNeeded = true;
        }
        if (updateNeeded){
            // Now update the material
            Color NewColor = new Color(newRGB, newRGB, newRGB, 1);
            Color NewTextColor = new Color(newTextRGB, newTextRGB, newTextRGB, 1);
            wallColor.SetColor("_Color", NewColor);
            Activity_Sign.GetComponent<TextMesh>().color = NewTextColor;
            Infos.GetComponent<TextMesh>().color = NewTextColor;
            currRGB = newRGB;
        }
    }
    void Update()
    {
        sensorReader.RefreshTrackedDevices();
        bool aButtonPressed = OVRInput.GetDown(OVRInput.Button.One, OVRInput.Controller.RTouch);
        bool bButtonPressed = OVRInput.GetDown(OVRInput.Button.Two, OVRInput.Controller.RTouch);
        bool frontRTriggerPressed = OVRInput.GetDown(OVRInput.Button.PrimaryIndexTrigger, OVRInput.Controller.RTouch);
        bool frontLTriggerPressed = OVRInput.GetDown(OVRInput.Button.PrimaryIndexTrigger, OVRInput.Controller.LTouch);
        bool xButtonPressed = OVRInput.GetDown(OVRInput.Button.One, OVRInput.Controller.LTouch);
        bool yButtonPressed = OVRInput.GetDown(OVRInput.Button.Two, OVRInput.Controller.LTouch);
        bool keyboardXPress = Input.GetKeyUp(KeyCode.X); 
        bool keyboardZPress = Input.GetKeyUp(KeyCode.Z);
        bool keyboardCPress = Input.GetKeyUp(KeyCode.C);
        bool keyboardVPress = Input.GetKeyUp(KeyCode.V);
        Color currColor = wallColor.GetColor("_Color");

        // triggers
        if (aButtonPressed | keyboardXPress) // toggle sleeping
        {
            UnityEngine.Debug.Log("Toggling sleep");
            isSleeping = !isSleeping;
            readyToDetect = isSleeping;
        }
        if (frontRTriggerPressed | keyboardCPress) // play alarm instantly
        {
            UnityEngine.Debug.Log("Playing alarm instantly");
            alarm.PlayOneShot(clip);
        }
        if (frontLTriggerPressed | keyboardZPress) // turn off alarm
        {   
            UnityEngine.Debug.Log("Turning off alarm; canceling alarm queues");
            alarm.Stop();
            timerActive = false;
        }
        if (xButtonPressed) // alarm in 1 minute
        {
            UnityEngine.Debug.Log("Alarm in 1 minute");
            timerActive = true;
            timeRemaining = 60.0f;
        }
        if (bButtonPressed | keyboardVPress) // jerryrigged alarm
        {
            alarm.PlayOneShot(clip);
            UnityEngine.Debug.Log("Jerryrigged alarm");
            timerActiveJR = true;
            timeRemainingJR = 15.0f;
        }
        
        if (timerActive)
        {
            timeRemaining -= Time.deltaTime;
            if (timeRemaining <= 0.0f)
            {
                alarm.PlayOneShot(clip);
                timerActive = false;
            }
        }

        if (timerActiveJR)
        {
            timeRemainingJR -= Time.deltaTime;
            if (timeRemainingJR < 0.0f)
            {
                alarm.PlayOneShot(clip);
                timerActiveJR = false;
            }
        }

        updateWallColor();  

        // Fetch attributes as a dictionary, with <device>_<measure> as a key
        // and Vector3 objects as values
        
        var attributes = sensorReader.GetSensorReadings();

        GetCurrentActivity(attributes);
        // Activity_Sign.GetComponent<TextMesh>().text = currentActivity;
    }
}