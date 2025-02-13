$(document).ready(function() {
    const table = $("#table_articles").DataTable({
        "paging": true,
        "ordering": true,
        "info": true,
        "language": {
            url: '//cdn.datatables.net/plug-ins/2.0.2/i18n/fr-FR.json',
        },
        "columnDefs": [
            { "orderable": false, "targets": [0, 3] }
        ]
    });

 $("#table_articles").on("click", "tr", function () {
        const row = table.row(this);
        const iconElement = $(this).find('.btn-more'); 
        if (row.child.isShown()) {
            row.child.hide();
            $(this).removeClass("shown");
            iconElement.removeClass("fa-chevron-down").addClass("fa-chevron-right");
        } else {
            const articleIndex = row.index();
            const article = articles[articleIndex];

            row.child(
                "<div class='moreInfo'>" +
                    "<strong>Description:</strong>" +
                    `${article.description}` + "<br>" +
                    "<strong>Date:</strong> " + `${article.date}` +
                "</div>"
            ).show();
            $(this).addClass("shown");
            iconElement.removeClass("fa-chevron-right").addClass("fa-chevron-down")
        }
    });
});
