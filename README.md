# [Bay Area Fear Free Vets Search App](https://bay-area-fear-free-vets.onrender.com)

This web application is designed to help pet parents with anxious pets find fear-free veterinarians (FF vets) in the Bay Area. By streamlining the search and decision-making process, this app simplifies the journey of finding the right care for your beloved pet.

------------------------------------------------------------------------------------------------------------------------------------

## Motivation

The official Fear Free (FF) website allows users to search for professionals (e.g., veterinarians, trainers, groomers) with FF certifications. However, it has significant limitations:

- **Disorganized Search Results:** Information is not well-structured, making it hard to compare options.
- **Lack of Reviews:** Users must independently research reviews, often using external search engines like Google.

This app addresses these pain points by integrating search, reviews, and useful features into one platform. Our goal is to save time for pet parents while providing a seamless experience.

------------------------------------------------------------------------------------------------------------------------------------

## Key Features

### Planned Features (Ultimate Vision)

The app aims to go beyond the functionality of the Fear Free website by offering:

1. **Enhanced Address Lookup:** Automatically fetch clinic addresses via Google for FF professionals without clear location details.
2. **Google Reviews Integration:** Display Google reviews for clinics and professionals (if available).
3. **Advanced Filtering:** Enable users to filter FF professionals based on specific criteria (e.g., location, specialty).
4. **Favorites Management:** Allow users to save FF professionals to a favorites list, with an option to email the list for easy reference.
5. **Community Reviews:** Build a platform where users can leave honest reviews, fostering trust and transparency.

------------------------------------------------------------------------------------------------------------------------------------

## Data

### Data Source

The data is sourced via web scraping from the [Fear Free website](https://fearfreepets.com/), focusing on FF vets located within approximately 100 miles of North San Jose, CA. Data is stored in a PostgreSQL database.

### Database Schema

For details on the database structure, refer to the `Schema.png` file in the repository.

------------------------------------------------------------------------------------------------------------------------------------

## Technology Stacks

### Development
This project was built with python 3.10.12 for the backend and javascript for the front end. Specifically, the backend was developed with Flask, SQLAlchemy and WTForms. The front end utilized [Bootstrap v5.3](https://getbootstrap.com/) and [Font Awesome](https://fontawesome.com/).

### Deployment
This project was deployed using [Supabase](https://supabase.com/) for the PostgreSQL database, [Gunicorn](https://gunicorn.org/) as the production server and [Render](https://render.com/) for serving the app from the cloud.

------------------------------------------------------------------------------------------------------------------------------------

## Current State

This app is currently in its initial stages of development, with features focused on FF veterinarians. As of now, it includes the following functionalities:

### Available Features

1. **Search Functionality:**

    - Users can search for FF vets by city or ZIP code.
    - Radius-based searches are under development.
    - This feature is open to all users without the need for login or signup.

2. **Favorites List:**

    - Logged-in users can save vets to their favorites list.
    - Email functionality to send the list is under development.

3. **User Reviews:**

    - Logged-in users can leave reviews for vets.
    - Reviews from Google are not yet integrated.

4. **Review Visibility:**

    - All users can view reviews for a specific vet.
    - Logged-in users can also view their own submitted reviews.

5. **Clinic Pages:**

    - Each clinic's page displays the number of FF vets associated with it.

------------------------------------------------------------------------------------------------------------------------------------

## Future Outlook

### Upcoming Enhancements

The following features are planned for future iterations:

- Radius-based search functionality.
- Automatic email functionality for favorites lists.
- Google reviews integration for clinics and professionals.
- Advanced filtering for FF professionals (e.g., by specialty or user ratings).
- Improved user interface and overall user experience.
- We are committed to making this app a valuable resource for pet parents and their anxious pets.

------------------------------------------------------------------------------------------------------------------------------------

## Contributing

Contributions are welcome! If you'd like to contribute, please fork the repository and create a pull request.

------------------------------------------------------------------------------------------------------------------------------------

## License
This project is licensed under the OrionsGuide LLC. 
