import turtle

canvas = turtle.Screen()
canvas.bgcolor("black")
canvas.title("Iron Man")

pen = turtle.Turtle()
pen.speed(0)
pen.color("red", "yellow")
pen.begin_fill()

for i in range(36):
    pen.forward(200)
    pen.left(170)

pen.end_fill()

turtle.done()
