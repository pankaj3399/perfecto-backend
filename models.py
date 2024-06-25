# models.py
from typing import List, Dict, Union, Any, Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class Property(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str
    image: str
    price: float
    address: str
    postalCode: str
    city: str
    region: str
    state: str
    beds: int
    baths: Union[int, float]
    sqft: int
    comingSoon: bool
    longitude: str
    latitude: str
    description: Optional[str]= Field(default=None)
    propertyListingDetails: Optional[Dict[str, str]]= Field(default=None)
    schools: Optional[List[Dict[str, str]]]= Field(default=None)
    amenities: Optional[Dict[str, str]]= Field(default=None)
    buildingInfo: Optional[Dict[str, str]]= Field(default=None)
    propertyHistory: Optional[List[Dict[str, str]]]= Field(default=None)
    homeFacts: Optional[Dict[str, str]]= Field(default=None)
    propertyInformation: Optional[Dict[str, Dict[str, Dict[str, Union[str, int]]]]]= Field(default=None)
    homeForSale: Optional[Any]= Field(default=None)
    publicRecords: Optional[Any]= Field(default=None)


    class Config:
        json_schema_extra = {
            "example": {
                "_id": "6661f687df143086619903c4",
                "id": 1,
                "name": "9 Mara Vista Court",
                "image": "https://example.com/image.jpg",
                "price": 2177000,
                "address": "9 Mara Vista Court, Tiburon, CA 94920",
                "postalCode": "94920",
                "city": "Tiburon",  
                "region": "Marin County",
                "state": "CA",
                "beds": 4,
                "baths": 2,
                "sqft": 1852,
                "comingSoon": True,
                "longitude": "-73.9855",
                "latitude": "40.7580",
                "description": "Description of the property.",
                "propertyListingDetails": {
                    "status": "Active",
                    "daysOnCompass": "-",
                    "taxes": "-",
                    "hoaFees": "-",
                    "condoCoopFees": "-",
                    "compassType": "Single Family",
                    "mlsType": "-",
                    "yearBuilt": "1954",
                    "lotSize": "0.17 AC / 7,210",
                    "county": "Marin County"
                },
                "schools": [
                    {
                        "rating": "8",
                        "name": "Reed Elementary School",
                        "type": "Public",
                        "gradesFrom": "K",
                        "gradesTo": "2",
                        "distance": "1.0"
                    },
                    {
                        "rating": "7",
                        "name": "Bel Aire Elementary School",
                        "type": "Public",
                        "gradesFrom": "3",
                        "gradesTo": "5",
                        "distance": "1.3"
                    },
                    {
                        "rating": "10",
                        "name": "Del Mar Middle School",
                        "type": "Public",
                        "gradesFrom": "6",
                        "gradesTo": "8",
                        "distance": "0.3"
                    },
                    {
                        "rating": "9",
                        "name": "Redwood High School",
                        "type": "Public",
                        "gradesFrom": "9",
                        "gradesTo": "12",
                        "distance": "4.1"
                    },
                    {
                        "rating": "7",
                        "name": "Another Elementary School",
                        "type": "Public",
                        "gradesFrom": "K",
                        "gradesTo": "5",
                        "distance": "2.0"
                    },
                    {
                        "rating": "6",
                        "name": "Another Middle School",
                        "type": "Public",
                        "gradesFrom": "6",
                        "gradesTo": "8",
                        "distance": "3.1"
                    },
                    {
                        "rating": "8",
                        "name": "Another High School",
                        "type": "Public",
                        "gradesFrom": "9",
                        "gradesTo": "12",
                        "distance": "5.1"
                    }
                ],
                "amenities": {
                    "backYard": "Built-Ins",
                    "carpetFloors": "Chandeliers",
                    "deck": "Dishwasher",
                    "electricStove": "Fence",
                    "fireplace": "Front Yard",
                    "gasOven": "Hardwood Floors",
                    "house": "Kitchen Dining",
                    "landmarkViews": "Oversized Windows",
                    "patio": "Primary Ensuite",
                    "pool": "Recessed Lighting"
                },
                "buildingInfo": {
                    "stories": "-",
                    "yearBuilt": "1954",
                    "buildingHeight": "-",
                    "lotSize": "0.17 AC / 7,210",
                    "buildingSize": "-",
                    "levelsStories": "-",
                    "seniorCommunity": "No",
                    "waterfrontFeatures": "Sewer Connected"
                },
                "propertyHistory": [
                    {
                        "date": "1995-09-10",
                        "eventAndSource": "Sold RESFAR #5013491",
                        "price": "447,600",
                        "appreciation": "0.0"
                    },
                    {
                        "date": "1995-11-09",
                        "eventAndSource": "Pending RESFAR #5013491",
                        "price": "447,600",
                        "appreciation": "0.0"
                    },
                    {
                        "date": "1995-08-14",
                        "eventAndSource": "Listed (Active) RESFAR #5013491",
                        "price": "459,000",
                        "appreciation": "0.0"
                    }
                ],
                "homeFacts": {
                    "beds": "4",
                    "yearBuilt": "1954",
                },
                "propertyInformation": {
                    "summary": {
                        "locationAndGeneralInformation": {
                            "areaDistrict": "Tiburon",
                            "areaShortDisplay": "A2600",
                            "areaLongDisplay": "Tiburon",
                            "propertyFaces": "Southwest"
                        },
                        "schoolInformation": {
                            "schoolDistrictCounty": "Marin",
                            "elementarySchoolDistrict": "Reed Union",
                            "middleOrJuniorSchoolDistrict": "Reed Union"
                        },
                        "parking": {
                            "parkingFeatures": "Converted Garage, Covered, Uncovered Parking Space",
                            "carportSpaces": 1,
                            "garageSpaces": 0,
                            "openParkingSpaces": 3
                        },
                        "taxesAndHOAInformation": {
                            "association": "No",
                            "associationFee": 0,
                            "apn": "055-183-15"
                        }
                    },
                    "propertyInfo": {
                        "lotInformation": {
                            "squareFootage": 1852,
                            "squareFootageSource": "Assessor Auto-Fill",
                            "yearBuiltSource": "Assessor Agent-Fill",
                            "lotSizeSource": "Assessor Auto-Fill",
                            "lotSizeSquareFeet": 7209,
                            "propertyCondition": "Updated/Remodeled"
                        },
                        "propertyAndAssessments": {
                            "securityFeatures": "Carbon Mon Detector, Smoke Detector",
                            "seniorCommunity": "No"
                        }
                    },
                    "interiorAndExteriorFeatures": {
                        "exteriorFeatures": {
                            "drivewaySidewalks": "Paved Sidewalk",
                            "fencing": "Full",
                            "foundation": "Concrete, Raised",
                            "horseProperty": "No",
                            "stories": 1,
                            "pool": "yes"
                        },
                        "interiorFeatures": {
                            "heating": "Central, Wall Furnace",
                            "cooling": "None",
                            "bathFeatures": "Stone, Tile, Tub w/Shower Over, Window",
                            "fullBathrooms": 2,
                            "diningRoomFeatures": "Formal Area"
                        }
                    }
                },
                "homeForSale": {
                    "title": "Homes for Sale near Tiburon",
                    "categories": [
                        {
                            "name": "Neighborhoods",
                            "links": [
                                "Belvedere Island",
                                "El Campo",
                                "Paradise Cay",
                                "Strawberry",
                                "The Lagoon"
                            ]
                        },
                        {
                            "name": "Cities",
                            "links": [
                                "Tiburon",
                                "Belvedere",
                                "Corte Madera",
                                "Mill Valley",
                                "Sausalito"
                            ]
                        },
                        {
                            "name": "ZIP Codes",
                            "links": [
                                "94920",
                                "94925",
                                "94941",
                                "94965",
                                "94970"
                            ]
                        }
                    ],
                    "disclaimer": "Some properties listed with participating firms do not appear on this website at the request of the seller."
                }
            }
        }

class ContactForm(BaseModel):
    name: str = Field(..., example="John Doe")
    email: str = Field(..., example="johndoe@example.com")
    phone: str = Field(..., example="123-456-7890")
    description: str = Field(..., example="I'm interested in one of your properties.")