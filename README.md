# Project README

## Introduction
This README provides an overview of the project, including design decisions, technology stack, deployment URL, user login instructions, and usage guide.

## Project Overview
The project aims to create a web application for managing items and user accounts. Users can view, create, update, and delete items, as well as manage their account information. The application also provides administrative capabilities for user management.

## Design Decisions
### Programming Language
Python was chosen as the primary programming language due to its simplicity, readability, and extensive ecosystem of libraries and frameworks suitable for web development.

### Frameworks
- Flask: Flask is a lightweight and flexible web framework for Python. It was chosen for its simplicity, ease of use, and ability to quickly build web applications.
- MongoDB: MongoDB(Atlas) was selected as the database management system due to its flexibility, scalability, and compatibility with Python through libraries such as PyMongo.

## Deployment
The application is deployed on Render. The deployment URL is [(https://e-marketplace-3.onrender.com)].

## User Login
- Authorized User: Users can log in using username(mail): "e2380533@ceng.metu.edu.tr" and password: 1547MR.mr credentials.
- Admin User: The admin user can log in using the predefined username "admin" and the corresponding password: 1547MR.mr  .

## Usage Guide
### User Management
- Upon logging in, authorized users can view, update, and delete their account information.
- The admin user has additional privileges to manage user accounts, including viewing and deleting user accounts.

### Item Management
- Users can view a list of available items on the homepage.
- They can create new items, update existing items, and delete items they have created.
- The application provides pagination for viewing items, with 10 items displayed per page.
- Items are listed from the most recent to the earliest.

### Favorite Items
- Users can add items to their favorites list by clicking the "Add to Favorites" button on the item details page.
- They can remove items from their favorites list by clicking the "Remove from Favorites" button.
- The application ensures that only active items are displayed on the homepage.

## Additional Information
- The project adheres to best practices for security, including password hashing and input validation.
- Error handling is implemented to provide informative messages to users in case of any issues.

## Support
For any questions, issues, or feedback, please contact [emre.kaplan@metu.edu.tr].

Thank you for using my application! I hope you find it useful and intuitive to use.