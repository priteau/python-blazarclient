(function(window, horizon, $, undefined) {
  'use strict';

  function init() {
    $.getJSON('/project/leases/calendar.json')
    .then(function(resp) {
      var tasks = $.map(resp.reservations, function(reservation, i) {
        return {
          'startDate': new Date(reservation.start_date),
          'endDate': new Date(reservation.end_date),
          'taskName': reservation.hypervisor_hostname,
          'status': reservation.status,
          'project': reservation.project_id
        }
      });

      var taskStatus = {
        'active': 'task-active',
        'pending': 'task-pending'
      };

      var taskNames = $.map(resp.compute_hosts, function(host, i) { return host.hypervisor_hostname; });

      tasks.sort(function(t0, t1) {
        return t0.endDate - t1.endDate;
      });

      var maxDate = tasks[tasks.length - 1].endDate;
      var minDate = tasks[0].startDate;

      var format = '%H:%M';

      var gantt = d3.gantt().taskTypes(taskNames).taskStatus(taskStatus).tickFormat(format);

      gantt(tasks);
    });
  }

  horizon.addInitFunction(init);

})(this, horizon, jQuery);
