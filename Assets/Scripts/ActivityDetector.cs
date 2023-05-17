using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using System;
using System.IO;
using System.Text;
using System.Diagnostics;
using System.ComponentModel;
using System.Reflection;
using UnityEngine;

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
    public GameObject Activity_Sign;
    public GameObject Infos;

    // Global Vars
    // Light vars
    private readonly double LIGHT_OFF_THRESHOLD = .05;
    private readonly double LIGHT_ON_THRESHOLD = .75;
    private readonly double LIGHT_OFF_DECAY = .99;
    private readonly double LIGHT_ON_GROWTH = 1.01;
    // recording vars
    private readonly int WINDOW_LENGTH = 5; // 5 seconds
    private bool readyToDetect = false;
    private float timeRemaining = 0;
    private bool timerActive = false;
    // other
    private string CURRDIRPATH = "";
    // private string PARENTDIRPATH = "";
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
    
    string GetCurrentActivity(Dictionary<string, Vector3> attributes)
    {
        if (!readyToDetect)
        {
            if (attributes_list.Count > 0)
            {
                attributes_list.Clear();
            }
            return "---";
        }
        // Store in attributes_list regardless of what we are about to do
        attributes_list.Add(attributes);
        // UnityEngine.Debug.Log("this0");
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
        string path = CURRDIRPATH + "/Assets/Resources/curr_data.csv";
        // Delete the file if exists
        if (File.Exists(path))
        {
            File.Delete(path);
        }

        string[] dimensions = {".x", ".y", ".z"};
        // Now create the csv file manually
        // temp123 = "ahere";
        try{
            using (StreamWriter writer = new StreamWriter(path))
            {   
                // temp123 = "bhere";
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
        }
        catch (Exception e)
        {
            // temp123 = e.Message;
            return "FAIL";
        }
        // Call the python script xD
        string detected_activity = "";
        // UnityEngine.Debug.Log("Starting python process!");
        ProcessStartInfo start = new ProcessStartInfo();
        start.FileName = EXEFILE_PATH; 
        start.UseShellExecute = false;
        start.RedirectStandardOutput = true;
        using(Process process = Process.Start(start))
        {
            using(StreamReader reader = process.StandardOutput)
            {
                detected_activity = reader.ReadToEnd();
            } 
        }
        // UnityEngine.Debug.Log("Detected Activity:");
        // UnityEngine.Debug.Log(detected_activity);
        // We've got some cleaning up to do
        attributes_list.RemoveRange(0, Math.Max(NUM_HZ, attributes_list.Count - (NUM_HZ * (WINDOW_LENGTH - 1))));
        prevActivity = detected_activity;

        return detected_activity;
    }
    // Start is called before the first frame update
    void Start()
    {
        sensorReader = new OculusSensorReader();
        CURRDIRPATH = Directory.GetCurrentDirectory();
        // /data/app/ (RANDOM LETTERS) / com.uchicago.mclabs-(randomletters) / base.apk/assets/bin/Data/Managed
        // CURRDIRPATH = "TEST";
        // CURRDIRPATH = "TESTING";
        // UnityEngine.Debug.Log("CURRDIRPATH:");
        // UnityEngine.Debug.Log(CURRDIRPATH);
        // PARENTDIRPATH = Directory.GetParent(CURRDIRPATH).ToString();
        // UnityEngine.Debug.Log("PARENTDIRPATH:");
        // UnityEngine.Debug.Log(PARENTDIRPATH);
        EXEFILE_PATH = CURRDIRPATH + "/Assets/Python/dist/testing_stuff";
        // UnityEngine.Debug.Log("EXEFILE_PATH:");
        // UnityEngine.Debug.Log(EXEFILE_PATH);

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
        bool frontRTriggerPressed = OVRInput.GetDown(OVRInput.Button.PrimaryIndexTrigger, OVRInput.Controller.RTouch);
        bool frontLTriggerPressed = OVRInput.GetDown(OVRInput.Button.PrimaryIndexTrigger, OVRInput.Controller.LTouch);
        bool xButtonPressed = OVRInput.GetDown(OVRInput.Button.One, OVRInput.Controller.LTouch);
        bool yButtonPressed = OVRInput.GetDown(OVRInput.Button.Two, OVRInput.Controller.LTouch);
        bool keyboardXPress = Input.GetKeyUp(KeyCode.X); 
        Color currColor = wallColor.GetColor("_Color");

        // triggers
        if (aButtonPressed | keyboardXPress) // toggle sleeping
        {
            // UnityEngine.Debug.Log("Toggling sleep");
            isSleeping = !isSleeping;
            readyToDetect = isSleeping;
        }
        if (frontRTriggerPressed) // play alarm instantly
        {
            // UnityEngine.Debug.Log("Playing alarm instantly");
            alarm.PlayOneShot(clip);
        }
        if (frontLTriggerPressed) // turn off alarm
        {   
            // UnityEngine.Debug.Log("Turning off alarm; canceling alarm queues");
            alarm.Stop();
            timerActive = false;
        }
        if (xButtonPressed) // alarm in 1 minute
        {
            UnityEngine.Debug.Log("Alarm in 1 minute");
            timerActive = true;
            timeRemaining = 60.0f;
        }
        if (yButtonPressed) // alarm in 5 minutes
        {
            UnityEngine.Debug.Log("Alarm in 5 minutes");
            timerActive = true;
            timeRemaining = 300.0f;
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

        updateWallColor();
        

        // Fetch attributes as a dictionary, with <device>_<measure> as a key
        // and Vector3 objects as values
        var attributes = sensorReader.GetSensorReadings();
        // prob start new thread here

        var currentActivity = GetCurrentActivity(attributes);
        try{
            string[] filess = Directory.GetDirectories(CURRDIRPATH, "*", SearchOption.AllDirectories);
            temp123 = "the directories:\n";
            foreach (string filezz in filess)
            {
                temp123 += filezz;
                temp123 += "\n";
            }
            
            // Update the Activity Sign text based on the detected activity
            
        }
        catch (Exception e)
        {
            temp123 = CURRDIRPATH + " " + e.Message;
        }
        Activity_Sign.GetComponent<TextMesh>().text = temp123;
    }
}