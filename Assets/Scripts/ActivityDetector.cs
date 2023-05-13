using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using System;
using System.IO;
using System.Text;
using System.Diagnostics;
using System.ComponentModel;
using System.Reflection;

public class ActivityDetector : MonoBehaviour
{
    public Material wallColor;

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
    private readonly int WINDOW_LENGTH = 5; // 5 seconds
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

        string[] dimensions = {".x", ".y", ".z"};
        // Now create the csv file manually
        using (StreamWriter writer = new StreamWriter(path))
        {   
            bool first_iter = true;
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
        float currRGB = currColor.r;
        float newRGB = 0;
        if(isSleeping && currRGB > 0)
        {
            // Turn lights off gradually
            if(currRGB < LIGHT_OFF_THRESHOLD)
            {
                newRGB = 0;
            }
            else
            {
                newRGB = currRGB * ((float) LIGHT_OFF_DECAY);
            }
        }
        else if(!isSleeping && currRGB < LIGHT_ON_THRESHOLD)
        {
            // Turn lights on gradually
            newRGB = (float) Math.Min(LIGHT_ON_THRESHOLD, currRGB * LIGHT_ON_GROWTH);
        }

        // Now update the material
        Color NewColor = new Color(newRGB, newRGB, newRGB, 1);
        wallColor.SetColor("_Color", NewColor);
    }
    void Update()
    {
        sensorReader.RefreshTrackedDevices();
        bool aButtonPressed = OVRInput.GetDown(OVRInput.Button.One, OVRInput.Controller.RTouch);
        bool frontRTriggerPressed = OVRInput.GetDown(OVRInput.Button.PrimaryIndexTrigger, OVRInput.Controller.RTouch);
        bool frontLTriggerPressed = OVRInput.GetDown(OVRInput.Button.PrimaryIndexTrigger, OVRInput.Controller.LTouch);
        Color currColor = wallColor.GetColor("_Color");

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