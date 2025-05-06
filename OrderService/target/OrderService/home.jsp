<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Home</title>
    
    <!-- Main CSS -->
    <link rel="stylesheet" href="css/style1.css">
    <style>
        /* Basic styling for the navbar */
        .navbar {
            background-color: #333;
            overflow: hidden;
            font-family: Arial, sans-serif;
        }

        .navbar ul {
            list-style-type: none;
            margin: 0;
            padding: 0;
        }

        .navbar li {
            float: left;
        }

        .navbar li a {
            display: block;
            color: white;
            text-align: center;
            padding: 14px 20px;
            text-decoration: none;
        }

        .navbar li a:hover {
            background-color: #575757;
        }

        .navbar .logout {
            float: right; /* Aligns the logout button to the right */
        }

        /* Styling for the welcome message */
        .welcome-container {
            text-align: center;
            margin-top: 50px;
            font-size: 36px; /* Increased font size for the welcome message */
            color: #333;
        }

        /* Paragraph styling */
        .welcome-container p {
            font-size: 20px; /* Increased font size for the paragraph */
            color: #555; /* Slightly lighter color for the paragraph */
            margin-top: 10px; /* Added margin for spacing */
            text-align: center; /* Centered paragraph text */
        }

        /* Styling for the body */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f7f6;
            margin: 0;
            padding: 0;
        }
    </style>
</head>
<body>

    <!-- Navigation bar -->
    <div class="navbar">
        <ul>
            <li><a href="home.jsp">Home</a></li>
            <li><a href="login.jsp">Profile</a></li>
            <li class="exit"><a href="index.jsp">Exit</a></li>
        </ul>
    </div>

    <!-- Welcome message -->
    <div class="welcome-container">
        <h1>Welcome, <%=session.getAttribute("1") %>!</h1>
        <p>We're glad to have you here. Explore your dashboard and manage your information...</p>
    </div>

</body>
</html>

