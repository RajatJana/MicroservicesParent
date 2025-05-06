package register;

import jakarta.servlet.RequestDispatcher;
import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;

/**
 * Servlet implementation class registerservlet
 */
@WebServlet("/register")
public class registrationServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;
    
	protected void doPost(HttpServletRequest request,HttpServletResponse response) throws ServletException, IOException {
		String uname = request.getParameter("name");
		String uemail = request.getParameter("email");
		String udob = request.getParameter("dob");
		String uempid = request.getParameter("empid");
		String umobile = request.getParameter("contact");
		
		HttpSession hs=request.getSession();
		hs.setAttribute("1", uname);
		hs.setAttribute("2", uemail);
		hs.setAttribute("3", udob);
		hs.setAttribute("4", uempid);
		hs.setAttribute("5", umobile);
		
		response.sendRedirect("login.jsp");
	}

}
