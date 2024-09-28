from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

def create_label_with_colored_text():
    label = QLabel()

    # Example of using HTML tags to color parts of the text
    label.setText('<span style="color: red;">This part is red, </span>'
                  '<span style="color: green;">this part is green, </span>'
                  '<span style="color: blue;">and this part is blue.</span>')

    return label

app = QApplication([])
window = QWidget()
layout = QVBoxLayout()

label = create_label_with_colored_text()
layout.addWidget(label)

window.setLayout(layout)
window.show()

app.exec_()
