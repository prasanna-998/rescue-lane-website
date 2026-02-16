
       
        const validUsername = "user123";
        const validPassword = "pass123";
    
        
        function validateLogin() {
          
          const username = document.getElementById('username').value;
          const password = document.getElementById('password').value;
          
          
          if (username === validUsername && password === validPassword) {
            alert("Login successful!");
            window.location.href = "/a_dashboard"; 
            return false;  
          } else {
            
            

            document.getElementById('errorMessage').textContent = "Invalid username or password!";
            return false; 
          }
        }
     