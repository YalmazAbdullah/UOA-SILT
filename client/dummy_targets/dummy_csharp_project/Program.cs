using System;
using System.Net.Sockets;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace DummyTest {
    
    internal static class Target {
        
        private const string _Host = "127.0.0.1";
        private const int _Port = 5000;

        private static void SendLog(string log) {
            
            try {
                
                var payload = new {
                    target_time = DateTimeOffset.UtcNow.ToString("o"),
                    source = "target",
                    target = "csharptest",
                    @event = "sending_log_csharp",
                    data = new {
                        message = log
                    }
                };

                string json = JsonSerializer.Serialize(payload);
                byte[] data = Encoding.UTF8.GetBytes(json);

                var client = new UdpClient();
                client.Send(data, data.Length, _Host, _Port);
            }

            catch (Exception ex) {
                Console.Error.WriteLine($"Failed to send UDP packet: {ex.Message}");
            }
        }

        static void Main(string[] args) {
            SendLog("Hello World");
        }
    }
}