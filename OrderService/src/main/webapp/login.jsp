<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="ie=edge">
<title>Profile</title>

<!-- Font Icon -->
<link rel="stylesheet"
	href="fonts/material-icon/css/material-design-iconic-font.min.css">

<!-- Main css -->
<link rel="stylesheet" href="css/style1.css">
</head>
<body>
   <nav class="navbar">
    <ul>
        <li><a href="home.jsp">Home</a></li>
        <li><a href="login.jsp">Profile</a></li>
        <li class="exit"><a href="index.jsp">Exit</a></li> 
    </ul>
</nav>


	<div class="container">
        <h1>EMPLOYEE INFORMATION</h1>
        <table>
            <tr>
                <th>Name</th>
                <td id="userName"><%=session.getAttribute("1") %></td>
            </tr>
            <tr>
                <th>Email</th>
                <td id="userEmail"><%=session.getAttribute("2") %></td>
            </tr>
            <tr>
                <th>Date of Birth</th>
                <td id="userDob"><%=session.getAttribute("3") %></td>
            </tr>
            <tr>
                <th>Employee ID</th>
                <td id="userEmpId"><%=session.getAttribute("4") %></td>
            </tr>
            <tr>
                <th>Mobile</th>
                <td id="userMobile"><%=session.getAttribute("5") %></td>
            </tr>
        </table>
    </div>

  

	<!-- JS -->
	<script src="vendor/jquery/jquery.min.js"></script>
	<script src="js/main.js"></script>
</body>
</html>