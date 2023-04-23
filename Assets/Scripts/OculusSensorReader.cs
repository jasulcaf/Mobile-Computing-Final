using System;
using System.IO;
using System.Collections.Generic;
using UnityEngine;

public class OculusSensorReader
{

    // List of logged sensor characteristics that are stored as 3D vectors
    public readonly Dictionary<String, UnityEngine.XR.InputFeatureUsage<UnityEngine.Vector3>> loggedVec3Characteristics;
    
    public readonly List<string> dimensions = new List<string>{"x", "y", "z"};

    private List<UnityEngine.XR.InputDevice> trackedDevices;
    

    public OculusSensorReader()
    {
        loggedVec3Characteristics = new Dictionary<String, UnityEngine.XR.InputFeatureUsage<UnityEngine.Vector3>> {
            {"vel", UnityEngine.XR.CommonUsages.deviceVelocity },
            {"angularVel", UnityEngine.XR.CommonUsages.deviceAngularVelocity },
            {"pos", UnityEngine.XR.CommonUsages.devicePosition },
        };

        RefreshTrackedDevices();
    }

    /// <summary>
    /// Reload the list of devices that have data logged based on connected devices.
    /// </summary>
    public void RefreshTrackedDevices()
    {
        trackedDevices = new List<UnityEngine.XR.InputDevice>();
        var desiredCharacteristics = UnityEngine.XR.InputDeviceCharacteristics.TrackedDevice;
        UnityEngine.XR.InputDevices.GetDevicesWithCharacteristics(desiredCharacteristics, trackedDevices);
    }

    public List<UnityEngine.XR.InputDevice> GetTrackedDevices()
    {
        return trackedDevices;
    }

    /// <summary>
    /// Fetch a list of available attributes, based on the current tracked devices,
    /// available attributes, and dimensions of each attribute.
    /// </summary>
    public List<string> GetAvailableAttributes() 
    {
        var attributes = new List<string>();
        foreach (var device in trackedDevices)
        {
            foreach (var key in loggedVec3Characteristics.Keys)
            {
                foreach (var axis in dimensions)
                {
                    attributes.Add($"{MapDeviceName(device.name)}_{key}.{axis}");
                }
            }
            foreach (var axis in dimensions)
            {
                attributes.Add($"{MapDeviceName(device.name)}_rot.{axis}");
            }
        }

        return attributes;
    }

    /// <summary>
    /// Fetch a dictionary of attributes and their corresponding sensor values
    /// at the time of the function call. Dictionary keys are named as <device>_<attribute>,
    /// with dimensions accessible through the returned Vector3 object.
    /// </summary>
    public Dictionary<string, Vector3> GetSensorReadings() 
    {
        var sensorReadings = new Dictionary<string, Vector3>();

        foreach (var device in trackedDevices)
        {
            Vector3 recordedValue;
            foreach (var characteristic in loggedVec3Characteristics) 
            {
                device.TryGetFeatureValue(characteristic.Value, out recordedValue);
                sensorReadings.Add($"{MapDeviceName(device.name)}_{characteristic.Key}", recordedValue);
            }

            // Rotation data is recorded as a quaternion, then converted into XYZ angles
            Quaternion rotationQuaternion;
            device.TryGetFeatureValue(UnityEngine.XR.CommonUsages.deviceRotation, out rotationQuaternion);
            recordedValue = rotationQuaternion.eulerAngles;
            sensorReadings.Add($"{MapDeviceName(device.name)}_rot", recordedValue);
        }

        return sensorReadings;
    }

    /// <returns>The CSV header string corresponding to a given Unity device name.</returns>
    string MapDeviceName(string deviceName)
    {
        if (deviceName.Contains("Left"))
        {
            return "controller_left";
        }

        if (deviceName.Contains("Right"))
        {
            return "controller_right";
        }

        if (deviceName.Contains("Quest"))
        {
            return "headset";
        }

        return "unknown";
    }
}