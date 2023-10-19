# Import the turtle module
import turtle

# Create a turtle object named 'drawer'
drawer = turtle.Turtle()

# Create a screen object named 's'
s = turtle.Screen()

# Set the background color of the screen to black
s.bgcolor("black")

# Lift the pen and move it to the starting position for the outer circle
drawer.penup()
drawer.setposition(-20, -350)

# Lower the pen and begin filling the circle with red color
drawer.pendown()
drawer.begin_fill()
drawer.color("red")
drawer.circle(300)
drawer.end_fill()

# Lift the pen and move it to the starting position for the inner circle
drawer.penup()
drawer.setposition(-20, -260)

# Lower the pen and begin filling the circle with black color
drawer.pendown()
drawer.begin_fill()
drawer.color("black")
drawer.circle(230)
drawer.end_fill()

# Lift the pen and move it to the starting position for the 'A' shape
drawer.penup()
drawer.setposition(0, -100)

# Lower the pen and begin filling the 'A' shape with red color
drawer.pendown()
drawer.begin_fill()
drawer.color("red")

# Set the pen size and color
drawer.pensize(2)
drawer.pencolor("grey")

# Draw the 'A' shape
drawer.backward(100)
drawer.left(60)
drawer.backward(200)
drawer.right(60)
drawer.backward(85)
drawer.right(115)
drawer.backward(600)
drawer.right(65)
drawer.backward(130)
drawer.right(90)
drawer.backward(440)
drawer.right(90)
drawer.backward(100)
drawer.right(90)
drawer.backward(65)

# End the fill for the 'A' shape
drawer.end_fill()

# Lift the pen and move it to the starting position for the 'V' shape
drawer.penup()
drawer.setposition(0, -50)

# Lower the pen and begin filling the 'V' shape with black color
drawer.pendown()
drawer.pensize(2)
drawer.begin_fill()
drawer.color("black")
drawer.pencolor("grey")

# Draw the 'V' shape
drawer.right(90)
drawer.forward(90)
drawer.right(120)
drawer.forward(170)
drawer.right(150)
drawer.forward(150)

# End the fill for the 'V' shape
drawer.end_fill()

# Keep the screen open after the logo has been drawn
turtle.done()
