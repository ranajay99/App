import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock

from kivy.lang import Builder

import requester

from graph import MeshLinePlot

interface = Builder.load_string('''
<AccelerometerDemo>:
    id:acc
    rows:4
    padding:15
    spacing:15
    font_size:5

    BoxLayout:
        spacing:10

        Graph:
            id: graph_plot1
            xlabel:'time'
            ylabel:'Engine_Load'
            y_grid_label: True
            x_grid_label: True
            xmin:0
            xmax:100
            ymin:0
            ymax:100

        Graph:
            id: graph_plot2
            xlabel:'time'
            ylabel:'KPL_Instant'
            y_grid_label: True
            x_grid_label: True
            xmin:0
            xmax:100
            ymin:0
            ymax:100

    BoxLayout:
        spacing:10

        Graph:
            id: graph_plot3
            xlabel:'time'
            ylabel:'Fuel_Flow'
            y_grid_label: True
            x_grid_label: True
            xmin:0
            xmax:100
            ymin:0
            ymax:200

        Graph:
            id: graph_plot4
            xlabel:'time'
            ylabel:'Air_Pedal'
            y_grid_label: True
            x_grid_label: True
            xmin:0
            xmax:100
            ymin:0
            ymax:100

        Graph:
            id: graph_plot5
            xlabel:'time'
            ylabel:'KPL_Instant'
            y_grid_label: True
            x_grid_label: True
            xmin:0
            xmax:100
            ymin:0
            ymax:200
        
    BoxLayout:
        spacing:10
        
        Button:
            size_hint_x: 0.2
            id: toggle_button
            text: 'START'
            on_press: root.do_toggle()

        Button:
            size_hint_x: 0.2
            id: toggle_button2
            text: 'PAUSE'
            on_press: root.do_toggle2()

    BoxLayout:
        spacing:10

        Graph:
            id: graph_plot0
            xlabel:'time'
            ylabel:'CO2_gkm_Instant'
            y_grid_label: True
            x_grid_label: True
            xmin:0
            xmax:100
            ymin:0
            ymax:1240

<ErrorPopup>:
    size_hint: .7, .4
    title: "Error"
    
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 20

        Label:
            size_hint_y: 0.4
            text: "This feature has not yet been implemented on this platform."
        Button:
            text: 'Dismiss'
            size_hint_y: 0.4
            on_press: root.dismiss()
            
    ''')

class AccelerometerDemo(GridLayout):
    def __init__(self):
        super().__init__()

        self.global_ind = 9

        self.BASE_URL = 'http://ec2-13-58-53-63.us-east-2.compute.amazonaws.com:8080/'
        self.payload = {'input':'900'}

        self.sensorEnabled = False
        self.graphs = []
        self.graphs.append(self.ids.graph_plot1)
        self.graphs.append(self.ids.graph_plot2)
        self.graphs.append(self.ids.graph_plot3)
        self.graphs.append(self.ids.graph_plot4)
        self.graphs.append(self.ids.graph_plot5)
        
        self.graph0 = self.ids.graph_plot0

        self.plot = []
        self.plot.append(MeshLinePlot(color=[0.8, 0.2, 0.2, 1]))  
        self.plot.append(MeshLinePlot(color=[0.8, 0.8, 0.2, 1]))  
        self.plot.append(MeshLinePlot(color=[0.4, 0.5, 0.9, 1]))
        self.plot.append(MeshLinePlot(color=[0.2, 0.4, 0.1, 1]))
        self.plot.append(MeshLinePlot(color=[0.9, 0.6, 0.2, 1]))

        self.outputplt = []
        self.outputplt.append(MeshLinePlot(color=[0.8, 0.5, 0.2, 1]))
        self.outputplt.append(MeshLinePlot(color=[0.1, 0.9, 0.7, 1]))

        self.reset_plots()

        for i in range(5):
            self.graphs[i].add_plot(self.plot[i])

        for op in self.outputplt:
            self.graph0.add_plot(op)

    def reset_plots(self):
        for plot in self.plot:
            plot.points = [(0, 0)]

        for plot in self.outputplt:
            plot.points = [(0, 0)]

        self.counter = 1

    def get_predicted(self):
        message = str(self.global_ind)
        self.payload['input'] = message

        data = requester.get(self.BASE_URL, params=self.payload)
        print('Received from server')  # show in terminal
        data = data.json()

        lst = []
        lst.append(data['x0'])
        lst.append(data['x1'])
        lst.append(data['x2'])
        lst.append(data['x3'])
        lst.append(data['x4'])
        lst.append(data['y'])
        lst.append(data['y_actual'])

        for i in range(7):
            lst[i] = float(lst[i])

        val = lst[:5]
        y_pred,y = lst[5],lst[6]

        return val,y_pred,y


    def do_toggle(self):
        try:
            if not self.sensorEnabled:
                Clock.schedule_interval(self.get_random, 1)

                self.sensorEnabled = True
                self.ids.toggle_button.text = "STOP"
            else:
                self.reset_plots()
                Clock.unschedule(self.get_random)
                
                self.sensorEnabled = False
                self.ids.toggle_button.text = "START"
        except NotImplementedError:
            popup = ErrorPopup()
            popup.open()

    def do_toggle2(self):
        if self.ids.toggle_button.text == "STOP":
            try:
                if not self.sensorEnabled:
                    Clock.schedule_interval(self.get_random, 1)

                    self.sensorEnabled = True
                    self.ids.toggle_button2.text = "PAUSE"
                else:
                    Clock.unschedule(self.get_random)

                    self.sensorEnabled = False
                    self.ids.toggle_button2.text = "PLAY"
            except NotImplementedError:
                popup = ErrorPopup()
                popup.open()

    def get_random(self, dt):
        if (self.counter == 100):
            # We re-write our points list if number of values exceed 100.
            # ie. Move each timestamp to the left.
            for plot in self.plot:
                del(plot.points[0])
                plot.points[:] = [(i[0] - 1, i[1]) for i in plot.points[:]]
            for plot in self.outputplt:
                del(plot.points[0])
                plot.points[:] = [(i[0] - 1, i[1]) for i in plot.points[:]]

            self.counter = 99

        val,y_pred,y_actual = self.get_predicted()

        for i in range(5):
            self.plot[i].points.append((self.counter, val[i]))

        self.outputplt[0].points.append((self.counter, y_pred)) ## orange
        self.outputplt[1].points.append((self.counter, y_actual)) ## blue

        self.counter += 1
        self.global_ind += 1

class AccelerometerDemoApp(App):
    def build(self):
        return AccelerometerDemo()

    def on_pause(self):
        return True


class ErrorPopup(Popup):
    pass


if __name__ == '__main__':
    AccelerometerDemoApp().run()