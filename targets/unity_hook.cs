using System;
using System.Collections.Generic;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

namespace SILT_Tools
{
    /// <summary>
    /// C# deafult serializer cant handle dicts. So we make a serializable struct ourselves and use it with lsit.
    /// </summary>
    [Serializable]
    public struct KeyValuePairData
    {
        public string key;
        public string value;
    }

    [Serializable]
    public class LogData
    {
        // Initialize lists and vars to avoid null serialization issues
        public string data = "";
        public List<string> data2 = new List<string>();
        public List<KeyValuePairData> data3 = new List<KeyValuePairData>();
    }

    [Serializable]
    public class LogPayload
    {
        public string target_time;
        public string source;
        public string target;
        public string @event;
        public LogData data;
    }

    public static class SILT_Logger
    {
        private const string Host = "127.0.0.1";
        private const int Port = 5000;
        private static readonly UdpClient Client = new UdpClient();

        /// <summary>
        /// Sends a log over UDP from any script.
        /// </summary>
        /// <param name="target">The game code and target component/system name (e.g., "DD_MainMenuUI", "DD_CombatSystem")</param>
        /// <param name="eventName">The type of event (e.g., "ui_click", "enemy_killed")</param>
        /// <param name="data">The event payload details</param>
        public static void Log(string target, string eventName, LogData data)
        {
            try
            {
                var payload = new LogPayload
                {
                    target_time = DateTimeOffset.UtcNow.ToString("o"),
                    source = "target",
                    target = target,
                    @event = eventName,
                    data = data
                };

                string json = JsonUtility.ToJson(payload);
                byte[] bytes = Encoding.UTF8.GetBytes(json);

                Client.Send(bytes, bytes.Length, Host, Port);
            }
            catch (Exception ex)
            {
                string error = string.Format("[SILT Telemetry] UDP send failed:", ex);
                Debug.LogError(error);
            }
        }
    }
}