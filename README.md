# AfroRecipeHub

AfroRecipeHub is a web-based platform designed to celebrate and share Afro-centric culinary traditions. Users can create, browse, and bookmark recipes, as well as engage with the community through comments. The platform includes comprehensive user management features, including admin oversight for content moderation.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [User Stories](#user-stories)
- [Technologies Used](#technologies-used)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Testing](#testing)
  - [Validation](#validation)
  - [Testing Write-up](#testing-write-up)
  - [Known Issues and Resolutions](#known-issues-and-resolutions)
  - [Additional Testing Information](#additional-testing-information)
- [Admin/Superuser Credentials](#adminsuperuser-credentials)
- [Screenshots](#screenshots)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

AfroRecipeHub is a community-driven platform where users can share and discover Afro-centric recipes. The platform provides a range of features, including recipe creation, user authentication, commenting, and bookmarking. Developed using Flask and MongoDB, AfroRecipeHub emphasizes user interaction and content management while fostering a community around Afro-centric culinary practices.

## Features

- **User Registration and Authentication**: Users can sign up, log in, and manage their profiles securely.
- **Recipe Management**: Users can add, edit, delete, and view recipes with ease.
- **Commenting System**: Users can comment on recipes, and admins have the ability to moderate these comments.
- **Bookmarking**: Users can bookmark their favorite recipes for quick access.
- **Admin Panel**: Admins can manage users, recipes, and comments to maintain the quality of the content.

## User Stories

- As a user, I want to register and log in to the platform so that I can access personalized features.
- As a user, I want to add new recipes so that I can share them with others.
- As a user, I want to edit and delete my recipes so that I can manage my content.
- As a user, I want to comment on recipes so that I can engage with the community.
- As a user, I want to bookmark recipes so that I can easily access them later.
- As an admin, I want to manage users and comments to maintain the quality of the content.

## Technologies Used

- **Flask**: A micro web framework used for developing the application.
- **MongoDB**: A NoSQL database used for storing user data, recipes, and comments.
- **Flask-Login**: For managing user sessions and authentication.
- **Flask-Bcrypt**: For securely hashing passwords.
- **Flask-WTF**: For form handling and CSRF protection.
- **Bootstrap**: For front-end styling and responsive design.

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/afrorecipehub.git
   cd afrorecipehub
