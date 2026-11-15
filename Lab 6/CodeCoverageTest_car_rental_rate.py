
import pytest
from car_rental_rate import (
    process_rental_fleet,
    check_fleet_telematics
)


def rental(**kwargs):
    data = {
        "is_confirmed": True,
        "vehicle_type": "economy",
        "driver_age": 30,
        "days": 2,
        "trip_segments": []
    }
    data.update(kwargs)
    return data


# Test invalid inputs
def test_invalid_rentals_type():
    with pytest.raises(ValueError):
        process_rental_fleet("invalid", 10)


def test_negative_admin_fee():
    with pytest.raises(ValueError):
        process_rental_fleet([], -1)


# Test rental confirmation
def test_unconfirmed_rental():
    result = process_rental_fleet(
        [rental(is_confirmed=False)], 10
    )
    assert result["status"] == "EMPTY_BATCH"


# Test invalid rental duration
def test_invalid_rental_days():
    result = process_rental_fleet(
        [rental(days=0)], 10
    )
    assert result["status"] == "EMPTY_BATCH"

    result = process_rental_fleet(
        [rental(days=-2)], 10
    )
    assert result["status"] == "EMPTY_BATCH"


# Test vehicle categories and driver age
def test_luxury_rental():
    result = process_rental_fleet(
        [rental(vehicle_type="luxury",
                driver_age=20, days=2)], 10
    )
    assert result["total_revenue"] == 350.0


def test_suv_rental():
    result = process_rental_fleet(
        [rental(vehicle_type="suv",
                driver_age=24, days=2)], 10
    )
    assert result["total_revenue"] == 190.0


def test_economy_young_driver():
    result = process_rental_fleet(
        [rental(vehicle_type="economy",
                driver_age=24, days=2)], 10
    )
    assert result["total_revenue"] == 130.0


# Test mileage conditions
def test_mileage_conditions():
    result = process_rental_fleet(
        [rental(trip_segments=[-5, 100, 301],
                driver_age=30)], 10
    )
    assert result["total_revenue"] == 230.4


def test_underage_high_mileage():
    result = process_rental_fleet(
        [rental(driver_age=20,
                trip_segments=[301, 100])], 10
    )
    assert result["total_revenue"] == 380.0


# Test risk status
def test_high_risk_audit():
    rentals = [rental(days=0) for _ in range(5)]
    result = process_rental_fleet(rentals, 10)
    assert result["status"] == "HIGH_RISK_AUDIT"


def test_standard_status():
    result = process_rental_fleet([rental()], 10)
    assert result["status"] == "STANDARD"


# Test fleet telematics
def test_telematics_no_data():
    assert check_fleet_telematics([]) == "NO_DATA"
    assert check_fleet_telematics(None) == "NO_DATA"


def test_telematics_safe():
    result = check_fleet_telematics(
        [[101, 90, 101], [100, 80]]
    )
    assert result == "SAFE"


def test_telematics_ground_vehicle():
    result = check_fleet_telematics([[101, 102]])
    assert result == "GROUND_VEHICLE"


def test_telematics_separate_vehicles():
    result = check_fleet_telematics([[101], [102]])
    assert result == "SAFE"
