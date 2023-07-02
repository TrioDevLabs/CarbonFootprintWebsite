function calculateTotalEmissions() {
    var total = parseFloat($("#propaneEm").text()) + parseFloat($("#oilEm").text()) + parseFloat($("#electricityEm").text()) + parseFloat($("#gasEm").text()) + parseFloat($("#veh-em").text());
    $('#total-em').text(total.toFixed(2));
}

$(function () {
    $("#form-total").steps({
        headerTag: "h2",
        bodyTag: "section",
        transitionEffect: "fade",
        enableAllSteps: true,
        autoFocus: true,
        transitionEffectSpeed: 500,
        titleTemplate: '<span class="title">#title#</span>',
        labels: {
            previous: 'Previous',
            next: 'Next Step',
            finish: 'Submit',
            current: ''
        },
        onStepChanged: function (event, currentIndex, priorIndex) {
            if (currentIndex === $("section").length - 1) {
                $(".actions .actions__finish").remove();
            }
        }
    });
});

$(document).ready(function () {
    var previousValue = 0;
    var newValue = 0;
    $('#vehicleNum').change(function () {
        newValue = parseInt($(this).val());

        if (newValue < previousValue) {
            var divsToRemove = previousValue - newValue;
            for (var i = 0; i < divsToRemove * 4; i++) {
                $('#vehiclePanel').children().last().remove();
            }
        }

        if (newValue > previousValue) {
            var start = previousValue + 1;
            for (var i = start; i <= newValue; i++) {
                var vehicleDiv = $('<div>').addClass('form-row');
                var vehicleTitle = $('<h5>').text('Vehicle ' + i);
                var milesFormRow = $('<div>').addClass('form-row');
                var milesFormHolder = $('<div>').addClass('form-holder');
                var milesCardBody = $('<div>').addClass('card-body').text('On average, miles you drive:');
                var milesInputHolder = $('<div>').addClass('form-holder');
                var milesInput = $('<input>').addClass('miles mile-input').attr('type', 'number').attr('name', 'miles' + i).attr('id', 'miles' + i).attr('min', '0').attr('oninput', 'this.value = Math.abs(this.value)').prop('required', true);
                var milesInputLabel = $('<span>').text(' Miles Per Year');
                var mileageFormRow = $('<div>').addClass('form-row');
                var mileageFormHolder = $('<div>').addClass('form-holder');
                var mileageCardBody = $('<div>').addClass('card-body').text('Average Gas Mileage:');
                var mileageInputHolder = $('<div>').addClass('form-holder');
                var mileageInput = $('<input>').addClass('miles mile-input').attr('type', 'number').attr('name', 'mileage' + i).attr('id', 'mileage' + i).attr('min', '0').attr('oninput', 'this.value = Math.abs(this.value)').prop('required', true);
                var mileageInputLabel = $('<span>').text(' Miles Per Gallon');


                $('#vehiclePanel').append(
                    $('<hr>'),
                    vehicleDiv.append(vehicleTitle),
                    milesFormRow.append(milesFormHolder.append(milesCardBody), milesInputHolder.append(milesInput, milesInputLabel)),
                    mileageFormRow.append(mileageFormHolder.append(mileageCardBody), mileageInputHolder.append(mileageInput, mileageInputLabel))
                );

            }
        }
        previousValue = parseInt($(this).val());
    });
    $('.propane-input').change(function () {
        var propane = $("#propane").val();
        var propaneType = $("#propane_type").val();
        var propaneEm = 12.43 * propane * 12;
        if (propaneType == 'Dollars') {
            propaneEm = propaneEm / 2.47;
        }
        $('#propaneEm').text(propaneEm.toFixed(2));
        calculateTotalEmissions();
    });
    $('.oil-input').change(function () {
        var oil = $("#oil").val();
        var oilType = $("#oil_type").val();
        var oilEm = 22.61 * oil * 12;
        if (oilType == 'Dollars') {
            oilEm = oilEm / 4.02;
        }
        $('#oilEm').text(oilEm.toFixed(2));
        calculateTotalEmissions();
    });
    $('.electricity-input').change(function () {
        var electricity = $("#electricity").val();
        var electricityType = $("#electricity_type").val();
        var electEm = electricity * 18.42 * 12;
        if (electricityType == 'Dollars') {
            electEm = electEm / 0.1188;
        }
        $('#electricityEm').text(electEm.toFixed(2));
        calculateTotalEmissions();
    });
    $('.gas-input').change(function () {
        var gas = $("#gas").val();
        var gasType = $("#gas_type").val();
        var gasEm = gas * 12;
        if (gasType == 'Therm') {
            gasEm = gasEm / 11.7;
        } else {
            gasEm = gasEm * 119.58;
        }
        if (gasType == 'Dollars') {
            gasEm = gasEm / 10.68;
        }
        $('#gasEm').text(gasEm.toFixed(2));
        calculateTotalEmissions();
    });
});

$(document).on('change', '.miles', function () {
    var totalEm = 0;
    console.log("Are u working??");
    for (var i = 1; i <= parseInt($('#vehicleNum').val()); i++) {
        var milesInput = parseFloat($('#miles' + i).val());
        var mileageInput = parseFloat($('#mileage' + i).val());
        var vehicleType = $('#vehicle_type').val();
        var vehicleEm = 0;
        if (vehicleType == 'Yes') {
            vehicleEm = (milesInput / mileageInput) * 19.6 * 1.01;
        } else {
            vehicleEm = (milesInput / mileageInput) * 19.6 * 1.01 * 11 / 10;
        }
        totalEm += vehicleEm;
    }
    $('#veh-em').text(totalEm.toFixed(2));
    calculateTotalEmissions();
});
