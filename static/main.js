
// clicking on "New Search?" will show the search form
const searchForm = $(".search-form");
const searchBtn = $(".new-search")
const recentBtn = $(".recent-searches")

function showSearchForm(evt) {
    searchBtn.hide();
    recentBtn.hide();
    searchForm.show();
}

searchBtn.on("click", showSearchForm);