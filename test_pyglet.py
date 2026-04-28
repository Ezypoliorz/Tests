import pyglet

window = pyglet.window.Window()
pyglet.gl.glClearColor(1,1,1,1)


label = pyglet.text.Label("Hello World !",
                          font_name='Arial',
                          font_size=20,
                          color=(0,0,0),
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')

square = pyglet.shapes.Rectangle(x=200, y=200, width=200, height=200, color=(55, 55, 255))

@window.event
def on_draw():
    window.clear()
    label.draw()

pyglet.app.run()
