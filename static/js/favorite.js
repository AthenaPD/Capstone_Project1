const $favorite = $("form[data-name = 'favorite']");
const $vets = $('#vets');
const $userName = $("#username");

async function handleFavorite(evt) {
    evt.preventDefault();

    // If user isn't logged in, promt user to log in or sign up else change favorite status
    if ($userName.length === 0) {
        if ($("#main div.alert.alert-danger").length === 0) {
            $("#main").prepend(
                `<div class='alert alert-danger mt-3'>
                Please <a href='/signup'>sign up</a> 
                or <a href="login">log in</a> 
                to save a vet to your favorite!</div>`);
        }
    } else {
        const vet_id = $(this).attr('id').substring(9);
        const resp = await axios.post(`${BASE_URL}/api/users/favorite/${vet_id}`);
        
        // change mark up with css
        if (resp.status === 200) {
            $(this).find(".btn").removeClass('btn-primary').addClass('btn-secondary');
        }

        if (resp.status === 201) {
            $(this).find(".btn").removeClass('btn-secondary').addClass('btn-primary');
        }
    }
}

$favorite.on("submit", handleFavorite);

async function markFavoriteVets() {
    const resp = await axios.get(`${BASE_URL}/api/users/favorites`);
    const favoriteVetIds = resp.data.favorite_vets.ids;
    
    // Change mark up of favorite vets
    for (let id of favoriteVetIds) {
        $(`#favorite-${id}`).find('.btn').removeClass('btn-secondary').addClass('btn-primary');
    }
}

// 1) Mark favorite vets 2) handle changing favorite status
// if the page contains vet info and if the user is logged in.
if ($vets.length !== 0 && $userName.length !== 0) {
    markFavoriteVets();
}
