using System;
using System.IO;
using System.Collections.Generic;
using UnityEngine;

public class OculusSensorCapture : MonoBehaviour
{
    OculusSensorReader sensorReader;

    private StreamWriter logWriter;
    private bool isLogging = false;
    
    private (string, string)[] activities = {("STD", "Get out of bed on feet"), ("SIT", "Sit up in bed"),
        ("LAY", "Laying on back"), ("ROL", "Roll in bed")};

    private int curActivityIdx = 0;
    
    private int curTrial = 0;

    private DateTime logStartTime;

    public TextMesh hudStatusText, wallStatusText, timerText;
    const string baseStatusText = "Press \"A\" to start/stop recording data.\n";

    // Start is called before the first frame update
    void Start()
    {
        sensorReader = new OculusSensorReader();
    }
    
    /// <summary>
    /// Get the filename prefix of a logged data file, based on the selected activity
    /// and group member.
    /// </summary>
    string GetDataFilePrefix()
    {
        return activities[curActivityIdx].Item1;
    }

    void StartLogging()
    {
        curTrial += 1;

        sensorReader.RefreshTrackedDevices();

        string filename = $"{GetDataFilePrefix()}_{curTrial:D2}.csv";
        string path = Path.Combine(Application.persistentDataPath, filename);
        
        logWriter = new StreamWriter(path);
        logWriter.WriteLine(GetLogHeader());
        
        logStartTime = DateTime.UtcNow;
        hudStatusText.text = baseStatusText + "STATUS: Recording";
    }

    void StopLogging()
    {
        logWriter.Close();
        hudStatusText.text = baseStatusText + "STATUS: Not recording";
    }

    /// <summary>
    /// Fetch the header of the CSV sensor log, based on the current tracked devices,
    /// available attributes, and dimensions of each attribute.
    /// </summary>
    string GetLogHeader() 
    {
        string logHeader = "time,";

        var attributes = sensorReader.GetAvailableAttributes();
        logHeader += String.Join(",", attributes);

        return logHeader;
    }

    /// <summary>Write the current sensor values to the open CSV file.</summary>
    void LogAttributes()
    {
        // Display the current time on the timer on the wall, then log it
        // in the CSV file
        TimeSpan timeDifference = DateTime.UtcNow - logStartTime;
        timerText.text = $"{timeDifference.TotalSeconds:F2} s";

        string logValue = $"{timeDifference.TotalMilliseconds},";
        
        var attributes = sensorReader.GetSensorReadings();
        foreach (var attribute in attributes)
        {
            logValue += $"{attribute.Value.x},{attribute.Value.y},{attribute.Value.z},";
        }

        logWriter.WriteLine(logValue);
    }

    /// <returns>The number of saved data files for the current user and activity.</returns>
    int GetNumExistingDataFiles()
    {
        var matchingFiles = Directory.GetFiles(Application.persistentDataPath, $"{GetDataFilePrefix()}*");
        return matchingFiles.Length;
    }

    /// <summary>
    /// Send a haptic vibration of the given amplitude and duration to all connected controllers.
    /// </summary>
    void SendImpulse(float amplitude, float duration)
    {
        foreach (var device in sensorReader.GetTrackedDevices())
        {
            if (device.TryGetHapticCapabilities(out var capabilities) &&
                capabilities.supportsImpulse)
            {
                device.SendHapticImpulse(0u, amplitude, duration);
            }
        }
    }

    // Update is called once per frame
    void Update()
    {
        // Check which buttons on the right controller are pressed on the current frame
        bool aButtonPressed = OVRInput.GetDown(OVRInput.Button.One, OVRInput.Controller.RTouch);
        bool frontTriggerPressed = OVRInput.GetDown(OVRInput.Button.PrimaryIndexTrigger, OVRInput.Controller.RTouch);
        
        // bool sideTriggerPressed = OVRInput.GetDown(OVRInput.Button.PrimaryHandTrigger, OVRInput.Controller.RTouch);

        // Change selected activity, send a small vibration for feedback,
        // and refresh the number of collected data files on the UI
        if (frontTriggerPressed)
        {
            curActivityIdx = (curActivityIdx + 1) % activities.Length;
            curTrial = GetNumExistingDataFiles();
            SendImpulse(0.1f, 0.05f);
        }

        // Change the wall UI text
        wallStatusText.text = $"Activity: {activities[curActivityIdx].Item2}\n" + 
            $"Last trial: {curTrial}"; 
        
        // Toggle logging on/off
        if (aButtonPressed)
        {
            isLogging = !isLogging;
            if (isLogging)
            {
                StartLogging();
            } else 
            {
                StopLogging();
            }

            SendImpulse(0.2f, 0.1f);
        }

        // Log attributes once for each frame if we are recording
        if (isLogging)
        {
            LogAttributes();
        }
    }
    
    /// <summary>
    /// Automatically close a log file if the app is closed while recording is in progress.
    /// Run when the scene is destroyed.
    /// </summary>
    void OnDestroy()
    {
        if (logWriter != null && logWriter.BaseStream != null)
        {
            logWriter.Close();
        }
    }

}
