import QtQuick 2.12

Rectangle {
    width: 480
    height: 272
    color: "black"

    Rectangle { x: 0;   y: 0; width: 160; height: 136; color: "red" }
    Rectangle { x: 160; y: 0; width: 160; height: 136; color: "green" }
    Rectangle { x: 320; y: 0; width: 160; height: 136; color: "blue" }
    Rectangle { x: 0;   y: 136; width: 160; height: 136; color: "white" }
    Rectangle { x: 160; y: 136; width: 160; height: 136; color: "yellow" }
    Rectangle { x: 320; y: 136; width: 160; height: 136; color: "magenta" }

    Text {
        anchors.centerIn: parent
        text: "Brewie Qt5 display test"
        color: "black"
        font.pixelSize: 22
    }
}
