This is a simple toolkit to help researchers interested in logging user interactions. The general architecture of this project is as illustrated below

<!-- Add image here for the architecture  -->

## Target
Target is the application that is being logged. Implement calls to the API in order to send data to the client or server. More on this shortly.

## Client
This serves as an intermeidary that can handle state and OS level logging. It recives logs and sends them over to the server. However it can be bypassed by implementing key calls directly into the target. 

## Server
The core of this toolkit is the server. It recives log data and writes it to a database. By default this is done with SQLite however by implementing the `abs_database_service` class you can change to a different service of your choice such as postgress. The server is also responsible for handling sessionization logic and making data available to the monitor GUI.

## Monitor
This is a simple GUI application that allows researchers to monitor the log data live as it comes in. This is particularly useful for testing logger implementation within the target. A target is whatever application you would like to log.