using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using System;
using System.IO;
using System.Text;

public class ActivityDetector : MonoBehaviour
{
    private Material wallColor;

    // public GameObject Wall1;
    // public GameObject Wall2;
    // public GameObject Wall3;
    // public GameObject Wall4;
    // public GameObject Ceiling;

    public AudioSource alarm;
    public AudioClip clip;

    // Global Vars
    private readonly double LIGHT_OFF_THRESHOLD = .05;
    private readonly double LIGHT_ON_THRESHOLD = .75;
    private readonly double LIGHT_OFF_DECAY = .9;
    private readonly double LIGHT_ON_GROWTH = 1.1;
    private readonly double WINDOW_LENGTH = 5; // 5 seconds
    private string PYFILE_PATH = "";

    OculusSensorReader sensorReader;
    
    int framesReceived = 0;
    int secTracker = 0;
    string prevActivity = "---";
    readonly int NUM_HZ = 72;
    List<Dictionary<string, Vector3>> attributes_list = new List<Dictionary<string, Vector3>>();
    private bool isSleeping = false;
    
    string GetCurrentActivity(Dictionary<string, Vector3> attributes)
    {
        // Store in attributes_list regardless of what we are about to do
        attributes_list.Add(attributes);
        if (framesReceived < NUM_HZ * WINDOW_LENGTH) // first three seconds of data
        {
            // Not ready to do our analysis. Return Unknown ("---")
            framesReceived++;
            secTracker++;
            return "---";
        }
        if (secTracker < NUM_HZ) // Already did an analysis within the last sec
        {
            framesReceived++;
            secTracker++;
            return prevActivity;
        }
        // Set these vars now so we dont have overlaps
        secTracker = 0;
        framesReceived ++;

        // We are ready to analyze the previous 3 seconds of data

        // write to csv so the python file can reference it
        string path = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location) + "curr_data.csv";
        // Delete the file if exists
        if (File.Exists(path))
        {
            File.Delete(path);
        }

        // Now create the csv file manually
        using (FileStream fs = File.Create(path))
        {
            foreach (var attributes in attributes_list)
            {
                if (attributes_list.First() == item)
                {
                    foreach (KeyValuePair<string, string> feature in attributes)
                    {
                        AddText(fs, feature.Item1);
                        AddText(fs, ",");
                    }
                    AddText(fs, "\n");
                }
                foreach (KeyValuePair<string, string> feature in attributes)
                {
                    AddText(fs, feature.Item2);
                    AddText(fs, ",");
                }
                AddText(fs, "\n");
            }
        }
        // Call the python script xD
        string detected_activity = "";
        ProcessStartInfo start = new ProcessStartInfo();
        start.FileName = PYFILE_PATH;
        start.UseShellExecute = false;
        start.RedirectStandardOutput = true;
        using(Process process = Process.Start(start))
        {
            using(StreamReader reader = process.StandardOutput)
            {
                detected_activity = reader.ReadToEnd();
            }
        }

        // We've got some cleaning up to do
        attributes_list.RemoveRange(0, Math.Max(NUM_HZ, attributes_list.Count - (NUM_HZ * (WINDOW_LENGTH - 1))));
        prevActivity = detected_activity;

        return detected_activity;
    }
    // Start is called before the first frame update
    void Start()
    {
        sensorReader = new OculusSensorReader();
        string CURRDIRPATH =  Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
        PYFILE_PATH = CURRDIRPATH.Substring(CURRDIRPATH.Length-7) + "Python/predict_continuous.py";
    }
    // void StartSleeping(Color CurrColor)
    // {
    //     wallColor
    // }
    // void StopSleeping(Color CurrColor)
    // {
        
    // }
    // Update is called once per frame
    void updateWallColor(Color currColor)
    {
        double currRGB = currColor.r;
        double newRGB = 0;
        if(isSleeping && currRGB > 0)
        {
            // Turn lights off gradually
            if(currRGB < LIGHT_OFF_THRESHOLD)
            {
                newRGB = 0;
            }
            else
            {
                newRGB = currRGB * LIGHT_OFF_DECAY;
            }
        }
        else if(!isSleeping && currRGB < LIGHT_ON_THRESHOLD)
        {
            // Turn lights on gradually
            newRGB = min(LIGHT_ON_THRESHOLD, currRGB * LIGHT_ON_GROWTH);
        }

        // Now update the material
        wallColor.SetColor(newRGB, newRGB, newRGB, 1);
    }
    void Update()
    {
        sensorReader.RefreshTrackedDevices();
        bool aButtonPressed = OVRInput.GetDown(OVRInput.Button.One, OVRInput.Controller.RTouch);
        bool frontRTriggerPressed = OVRInput.GetDown(OVRInput.Button.PrimaryIndexTrigger, OVRInput.Controller.RTouch);
        bool frontLTriggerPressed = OVRInput.GetDown(OVRInput.Button.PrimaryIndexTrigger, OVRInput.Controller.LTouch);
        Color currColor = Material.GetColor("_Color");

        // triggers
        if (aButtonPressed)
        {
            isSleeping = !isSleeping;
        }
        if (frontRTriggerPressed)
        {
            alarm.PlayOneShot(clip);
        }
        if (frontLTriggerPressed)
        {   
            alarm.Stop();
        }

        updateWallColor(currColor);

        // Fetch attributes as a dictionary, with <device>_<measure> as a key
        // and Vector3 objects as values
        var attributes = sensorReader.GetSensorReadings();

        var currentActivity = GetCurrentActivity(attributes);

        

        // Update the Activity Sign text based on the detected activity
        // Activity_Sign.GetComponent<TextMesh>().text = currentActivity;
    }
}