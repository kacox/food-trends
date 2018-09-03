// clicking on "New Search?" will show the search form
const searchForm = $("#search-form");
const searchBtn = $("#new-search")
const recentBtn = $("#recent-searches")

function showSearchForm() {
    console.log("Inside fxn");
    searchBtn.hide();
    recentBtn.hide();
    searchForm.removeAttr("hidden");
}

searchBtn.submit(function( event ) {
    // debugger;
  showSearchForm();
  event.preventDefault();
});