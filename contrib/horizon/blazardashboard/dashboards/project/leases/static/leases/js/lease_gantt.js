(function(window, horizon, $, undefined) {
  'use strict';

  function init() {
    var gantt;
    var tasks;
    var form;

    $.getJSON('../calendar.json')
    .done(function(resp) {

      tasks = resp.reservations.map(function(reservation, i) {
        reservation.hosts = resp.reservations.filter(
          function(r) {
            return r.id === this.id;
          },
          reservation
        ).map(function(h) { return h.hypervisor_hostname; });

        return {
          'startDate': new Date(reservation.start_date),
          'endDate': new Date(reservation.end_date),
          'taskName': reservation.hypervisor_hostname,
          'status': reservation.status,
          'data': reservation
        }
      });

      var taskStatus = {
        'active': 'task-active',
        'pending': 'task-pending'
      };

      var taskNames = $.map(resp.compute_hosts, function(host, i) {
        return host.hypervisor_hostname;
      });

      var format = '%d-%b %H:%M';
      $('#blazar-gantt').empty().height(20 * taskNames.length);
      gantt = d3.gantt({
        selector:'#blazar-gantt',
        taskTypes: taskNames,
        taskStatus: taskStatus,
        tickFormat: format
      });
      gantt(tasks);

      /* set initial time range */
      setTimeDomain(gantt.timeDomain());
    })
    .fail(function() {
      $('#blazar-gantt').html('<div class="alert alert-danger">Unable to load reservations.</div>');
    });

    function setTimeDomain(timeDomain) {
      form.removeClass('time-domain-processed');
      $('#dateStart').datepicker('setDate', timeDomain[0]);
      $('#timeStartHours').val(timeDomain[0].getHours());
      $('#timeStartMinutes').val(timeDomain[0].getMinutes());
      $('#dateEnd').datepicker('setDate', timeDomain[1]);
      $('#timeEndHours').val(timeDomain[1].getHours());
      $('#timeEndMinutes').val(timeDomain[1].getMinutes());
      form.addClass('time-domain-processed');
    }

    function getTimeDomain() {
      var timeDomain = [
        $('#dateStart').datepicker('getDate'),
        $('#dateEnd').datepicker('getDate')
      ];

      timeDomain[0].setHours($('#timeStartHours').val());
      timeDomain[0].setMinutes($('#timeStartMinutes').val());
      timeDomain[1].setHours($('#timeEndHours').val());
      timeDomain[1].setMinutes($('#timeEndMinutes').val());

      return timeDomain;
    }

    function redraw() {
      if (gantt && tasks) {
        gantt.redraw(tasks);
      }
    }

    $(window).on('resize', redraw);

    form = $('form[name="blazar-gantt-controls"]');

    $('input[data-datepicker]', form).datepicker({
      dateFormat: 'mm/dd/yyyy'
    });

    $('input', form).on('change', function() {
      if (form.hasClass('time-domain-processed')) {
        var timeDomain = getTimeDomain();
        if (timeDomain[0] >= timeDomain[1]) {
          timeDomain[1] = d3.time.day.offset(timeDomain[0], +1);
          setTimeDomain(timeDomain);
        }
        gantt.timeDomain(timeDomain);
        redraw();
      }
    });
  }

  horizon.addInitFunction(init);

})(window, horizon, jQuery);
