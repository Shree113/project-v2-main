(function () {
  'use strict';

  function init() {
    var select = document.getElementById('id_round_number');
    if (!select) return;

    select.addEventListener('change', function () {
      var round = this.value;   // "1" or "2"
      var url   = window.location.pathname;
      window.location.href = url + '?round_number=' + round;
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();