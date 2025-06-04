document.addEventListener("DOMContentLoaded", function() {
  var loader = document.getElementById("load");

  // Show the loader
  loader.style.display = "block";

  // Delay hiding the loader
  setTimeout(function() {
    // Hide the loader after 4 seconds
    loader.style.display = "none";
  }, 4000); // 3000 milliseconds = 4 seconds
});


document.addEventListener('DOMContentLoaded', function () {
    const toggleSidebarBtn = document.getElementById('toggleSidebarBtn');
    const sidebar = document.getElementById('sidebar');
    const main = document.getElementById('main');
  
    // Store the original margin of the main element
    const originalMainMarginLeft = window.getComputedStyle(main).marginLeft;
  
    let isSidebarVisible = window.innerWidth > 575;
  
    toggleSidebarBtn.addEventListener('click', function () {
        if (sidebar.style.display === 'none' && window.innerWidth <= 575) {
            sidebar.style.display = 'block';
            main.style.marginLeft = '150px';

        } else if (window.innerWidth > 575){
            sidebar.style.display = 'none';
            main.style.marginLeft = originalMainMarginLeft;

        }
        else {
            sidebar.style.display = 'none';
            main.style.marginLeft = '-110px';
        }
    });
  
    // Ensure sidebar is hidden on small screens initially
    if (window.innerWidth <= 575) {
        sidebar.style.display = 'none';
        main.style.marginLeft = originalMainMarginLeft;
        isSidebarVisible = false;
    }
    else {
        sidebar.style.display = 'block';
        isSidebarVisible = true;
    }
  
    // Toggle sidebar visibility on window resize
    window.addEventListener('resize', function () {
        if (window.innerWidth <= 575) {
            sidebar.style.display = 'none';
            main.style.marginLeft = originalMainMarginLeft;
            isSidebarVisible = false;
        } else {
            if (isSidebarVisible) {
                sidebar.style.display = 'block';
                main.style.marginLeft = '150px';
            } else {
                sidebar.style.display = 'block';
                main.style.marginLeft = originalMainMarginLeft;
            }
        }
    });
  });