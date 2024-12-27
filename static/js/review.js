const $reviewCommentsMore = $("p[id|='review-comment'] span");

async function handleMore(evt) {
    evt.preventDefault();

    // Get full comment
    const $commentParagraph = $(this).parent();
    const review_id = $commentParagraph.attr('id').substring(15);
    const resp = await axios.get(`${BASE_URL}/api/reviews/${review_id}`);
    const fullComment = resp.data.review.comment;
    $commentParagraph.text(fullComment);
}

$reviewCommentsMore.on('click', handleMore)