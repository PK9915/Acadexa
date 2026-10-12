/* =========================================================
   Acadexa
   Student Assignment & Notes Management System

   JavaScript Frontend Controller
========================================================= */


/* =========================================================
   1. WAIT FOR PAGE TO LOAD
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    console.log("Acadexa application loaded successfully.");



    /* =====================================================
       2. SELECT IMPORTANT ELEMENTS
    ===================================================== */

    const navbar =
        document.querySelector(".navbar");

    const mobileMenu =
        document.getElementById("mobileMenu");

    const navMenu =
        document.querySelector(".nav-menu");

    const backToTop =
        document.getElementById("backToTop");



    /* =====================================================
       3. NAVBAR SCROLL EFFECT
    ===================================================== */

    function handleNavbarScroll() {

        if (window.scrollY > 40) {

            navbar.classList.add("scrolled");

        } else {

            navbar.classList.remove("scrolled");

        }

    }


    window.addEventListener(
        "scroll",
        handleNavbarScroll
    );


    handleNavbarScroll();



    /* =====================================================
       4. MOBILE NAVIGATION
    ===================================================== */

    if (mobileMenu && navMenu) {

        mobileMenu.addEventListener(
            "click",
            function () {

                navMenu.classList.toggle("mobile-active");


                const icon =
                    mobileMenu.querySelector("i");


                if (
                    navMenu.classList.contains(
                        "mobile-active"
                    )
                ) {

                    icon.classList.remove(
                        "fa-bars"
                    );

                    icon.classList.add(
                        "fa-xmark"
                    );

                } else {

                    icon.classList.remove(
                        "fa-xmark"
                    );

                    icon.classList.add(
                        "fa-bars"
                    );

                }

            }
        );

    }



    /* =====================================================
       5. CLOSE MOBILE MENU WHEN LINK IS CLICKED
    ===================================================== */

    const navLinks =
        document.querySelectorAll(
            ".nav-link"
        );


    navLinks.forEach(
        function (link) {

            link.addEventListener(
                "click",
                function () {

                    navLinks.forEach(
                        function (item) {

                            item.classList.remove(
                                "active"
                            );

                        }
                    );


                    this.classList.add(
                        "active"
                    );


                    if (navMenu) {

                        navMenu.classList.remove(
                            "mobile-active"
                        );

                    }


                    if (mobileMenu) {

                        const icon =
                            mobileMenu.querySelector(
                                "i"
                            );


                        if (icon) {

                            icon.classList.remove(
                                "fa-xmark"
                            );

                            icon.classList.add(
                                "fa-bars"
                            );

                        }

                    }

                }
            );

        }
    );



    /* =====================================================
       6. ACTIVE NAVIGATION ON SCROLL
    ===================================================== */

    const sections =
        document.querySelectorAll(
            "section[id]"
        );


    function updateActiveNavigation() {

        let currentSection = "";


        sections.forEach(
            function (section) {

                const sectionTop =
                    section.offsetTop - 150;


                const sectionHeight =
                    section.offsetHeight;


                if (
                    window.scrollY >= sectionTop &&
                    window.scrollY <
                    sectionTop + sectionHeight
                ) {

                    currentSection =
                        section.getAttribute("id");

                }

            }
        );


        navLinks.forEach(
            function (link) {

                link.classList.remove(
                    "active"
                );


                const href =
                    link.getAttribute("href");


                if (
                    href === "#" +
                    currentSection
                ) {

                    link.classList.add(
                        "active"
                    );

                }

            }
        );

    }


    window.addEventListener(
        "scroll",
        updateActiveNavigation
    );



    /* =====================================================
       7. BACK TO TOP BUTTON
    ===================================================== */

    function handleBackToTop() {

        if (!backToTop) {
            return;
        }


        if (window.scrollY > 500) {

            backToTop.classList.add(
                "show"
            );

        } else {

            backToTop.classList.remove(
                "show"
            );

        }

    }


    window.addEventListener(
        "scroll",
        handleBackToTop
    );


    handleBackToTop();


    if (backToTop) {

        backToTop.addEventListener(
            "click",
            function () {

                window.scrollTo({

                    top: 0,

                    behavior: "smooth"

                });

            }
        );

    }



    /* =====================================================
       8. SMOOTH SCROLL FOR INTERNAL LINKS
    ===================================================== */

    const internalLinks =
        document.querySelectorAll(
            'a[href^="#"]'
        );


    internalLinks.forEach(
        function (link) {

            link.addEventListener(
                "click",
                function (event) {

                    const targetID =
                        this.getAttribute(
                            "href"
                        );


                    if (
                        targetID === "#" ||
                        targetID === ""
                    ) {

                        return;

                    }


                    const target =
                        document.querySelector(
                            targetID
                        );


                    if (target) {

                        event.preventDefault();


                        const navbarHeight =
                            navbar
                                ? navbar.offsetHeight
                                : 0;


                        const targetPosition =
                            target.offsetTop -
                            navbarHeight;


                        window.scrollTo({

                            top:
                                targetPosition,

                            behavior:
                                "smooth"

                        });

                    }

                }
            );

        }
    );



    /* =====================================================
       9. FEATURE CARD ANIMATION
    ===================================================== */

    const featureCards =
        document.querySelectorAll(
            ".feature-card"
        );


    featureCards.forEach(
        function (card, index) {

            card.style.opacity = "0";

            card.style.transform =
                "translateY(25px)";


            card.style.transition =
                "opacity 0.6s ease " +
                (index * 0.08) +
                "s, transform 0.6s ease " +
                (index * 0.08) +
                "s";

        }
    );



    /* =====================================================
       10. INTERSECTION OBSERVER
    ===================================================== */

    const observerOptions = {

        threshold: 0.12

    };


    const revealObserver =
        new IntersectionObserver(
            function (entries) {

                entries.forEach(
                    function (entry) {

                        if (
                            entry.isIntersecting
                        ) {

                            entry.target.style.opacity =
                                "1";

                            entry.target.style.transform =
                                "translateY(0)";

                            revealObserver.unobserve(
                                entry.target
                            );

                        }

                    }
                );

            },
            observerOptions
        );



    featureCards.forEach(
        function (card) {

            revealObserver.observe(
                card
            );

        }
    );



    /* =====================================================
       11. WORKFLOW ANIMATION
    ===================================================== */

    const workflowSteps =
        document.querySelectorAll(
            ".workflow-step"
        );


    workflowSteps.forEach(
        function (step, index) {

            step.style.opacity =
                "0";

            step.style.transform =
                "translateY(20px)";

            step.style.transition =
                "opacity 0.6s ease " +
                (index * 0.12) +
                "s, transform 0.6s ease " +
                (index * 0.12) +
                "s";


            revealObserver.observe(
                step
            );

        }
    );



    /* =====================================================
       12. STATISTICS COUNTER
    ===================================================== */

    const statNumbers =
        document.querySelectorAll(
            ".stat-box strong"
        );


    function animateCounter(element) {

        const originalText =
            element.textContent.trim();


        const numberMatch =
            originalText.match(
                /[\d]+/
            );


        if (!numberMatch) {
            return;
        }


        const targetNumber =
            parseInt(
                numberMatch[0],
                10
            );


        const suffix =
            originalText.replace(
                numberMatch[0],
                ""
            );


        let currentNumber = 0;


        const duration = 1200;

        const intervalTime = 20;

        const increment =
            targetNumber /
            (duration / intervalTime);


        const counter =
            setInterval(
                function () {

                    currentNumber +=
                        increment;


                    if (
                        currentNumber >=
                        targetNumber
                    ) {

                        currentNumber =
                            targetNumber;

                        clearInterval(
                            counter
                        );

                    }


                    element.textContent =
                        Math.floor(
                            currentNumber
                        ) +
                        suffix;

                },
                intervalTime
            );

    }



    const statisticsSection =
        document.querySelector(
            ".stats-section"
        );


    if (statisticsSection) {

        let counterStarted =
            false;


        const statisticsObserver =
            new IntersectionObserver(
                function (entries) {

                    entries.forEach(
                        function (entry) {

                            if (
                                entry.isIntersecting &&
                                !counterStarted
                            ) {

                                counterStarted =
                                    true;


                                statNumbers.forEach(
                                    function (
                                        number
                                    ) {

                                        animateCounter(
                                            number
                                        );

                                    }
                                );


                                statisticsObserver.unobserve(
                                    statisticsSection
                                );

                            }

                        }
                    );

                },
                {
                    threshold: 0.3
                }
            );


        statisticsObserver.observe(
            statisticsSection
        );

    }



    /* =====================================================
       13. FEATURE CARD TILT EFFECT
    ===================================================== */

    featureCards.forEach(
        function (card) {

            card.addEventListener(
                "mousemove",
                function (event) {

                    const rect =
                        card.getBoundingClientRect();


                    const x =
                        event.clientX -
                        rect.left;


                    const y =
                        event.clientY -
                        rect.top;


                    const centerX =
                        rect.width / 2;


                    const centerY =
                        rect.height / 2;


                    const rotateX =
                        ((y - centerY) /
                        centerY) *
                        -2;


                    const rotateY =
                        ((x - centerX) /
                        centerX) *
                        2;


                    card.style.transform =
                        "translateY(-7px) " +
                        "perspective(700px) " +
                        "rotateX(" +
                        rotateX +
                        "deg) " +
                        "rotateY(" +
                        rotateY +
                        "deg)";

                }
            );


            card.addEventListener(
                "mouseleave",
                function () {

                    card.style.transform =
                        "translateY(0)";

                }
            );

        }
    );



    /* =====================================================
       14. DASHBOARD MOUSE EFFECT
    ===================================================== */

    const dashboard =
        document.querySelector(
            ".dashboard-window"
        );


    if (dashboard) {

        dashboard.addEventListener(
            "mousemove",
            function (event) {

                const rect =
                    dashboard.getBoundingClientRect();


                const x =
                    event.clientX -
                    rect.left;


                const y =
                    event.clientY -
                    rect.top;


                const centerX =
                    rect.width / 2;


                const centerY =
                    rect.height / 2;


                const rotateY =
                    ((x - centerX) /
                    centerX) *
                    3;


                const rotateX =
                    ((y - centerY) /
                    centerY) *
                    -3;


                dashboard.style.transform =
                    "perspective(1200px) " +
                    "rotateX(" +
                    rotateX +
                    "deg) " +
                    "rotateY(" +
                    rotateY +
                    "deg)";

            }
        );


        dashboard.addEventListener(
            "mouseleave",
            function () {

                dashboard.style.transform =
                    "perspective(1200px) " +
                    "rotateY(-4deg) " +
                    "rotateX(2deg)";

            }
        );

    }



    /* =====================================================
       15. BUTTON CLICK FEEDBACK
    ===================================================== */

    const buttons =
        document.querySelectorAll(
            ".btn"
        );


    buttons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    this.classList.add(
                        "button-clicked"
                    );


                    setTimeout(
                        () => {

                            this.classList.remove(
                                "button-clicked"
                            );

                        },
                        250
                    );

                }
            );

        }
    );



    /* =====================================================
       16. SECURITY SECTION REVEAL
    ===================================================== */

    const securitySection =
        document.querySelector(
            ".security-container"
        );


    if (securitySection) {

        securitySection.style.opacity =
            "0";

        securitySection.style.transform =
            "translateY(30px)";

        securitySection.style.transition =
            "opacity 0.8s ease, " +
            "transform 0.8s ease";


        revealObserver.observe(
            securitySection
        );

    }



    /* =====================================================
       17. ABOUT SECTION REVEAL
    ===================================================== */

    const aboutContent =
        document.querySelector(
            ".about-content"
        );


    if (aboutContent) {

        aboutContent.style.opacity =
            "0";

        aboutContent.style.transform =
            "translateX(30px)";

        aboutContent.style.transition =
            "opacity 0.8s ease, " +
            "transform 0.8s ease";


        revealObserver.observe(
            aboutContent
        );

    }



    /* =====================================================
       18. CONSOLE PROJECT INFORMATION
    ===================================================== */

    console.log(
        "======================================"
    );

    console.log(
        "Acadexa Student Portal"
    );

    console.log(
        "Frontend initialized successfully"
    );

    console.log(
        "Technology: HTML + CSS + JavaScript"
    );

    console.log(
        "Backend: Python Flask"
    );

    console.log(
        "Database: MySQL (coming next)"
    );

    console.log(
        "======================================"
    );

});