# Data Formats Design Document

**Version:** 1.0  
**Date:** November 22, 2025  
**Status:** Design Phase  

## 1. Overview

This document defines the data formats for storing Game Data, Gene Data, and Gene Preference data in TurboShells. These formats ensure consistency, performance, and maintainability across the save system and data management.

### 1.1 Goals
- **Consistency**: Standardized format across all data types
- **Performance**: Optimized for fast serialization/deserialization
- **Extensibility**: Easy to add new fields without breaking compatibility
- **Validation**: Built-in data integrity checks
- **Human Readable**: JSON format for debugging and inspection

### 1.2 Scope
- Game state persistence
- Genetic data storage
- Player preference tracking
- Voting system data
- Performance metrics

---

## 2. Game Data Format

### 2.1 Root Game Data Structure
```json
{
  "version": "2.2.0",
  "timestamp": "2025-11-22T23:09:00Z",
  "player_id": "player_12345",
  "game_state": {
    "money": 1250,
    "current_phase": "ROSTER",
    "unlocked_features": ["voting", "breeding", "advanced_genetics"],
    "tutorial_progress": {
      "roster_intro": true,
      "racing_basics": true,
      "breeding_intro": false,
      "voting_system": true
    },
    "session_stats": {
      "total_playtime_minutes": 1250,
      "races_completed": 45,
      "turtles_bred": 12,
      "votes_cast": 23
    }
  },
  "roster": {
    "active_slots": 3,
    "active_turtles": ["turtle_001", "turtle_002", "turtle_003"],
    "retired_turtles": ["turtle_004", "turtle_005", "turtle_006"],
    "max_retired": 20
  },
  "last_sessions": [
    {
      "timestamp": "2025-11-22T22:30:00Z",
      "duration_minutes": 45,
      "activities": ["racing", "voting", "breeding"]
    }
  ]
}
```

### 2.2 Economic Data
```json
{
  "economy": {
    "total_earned": 5000,
    "total_spent": 3750,
    "transaction_history": [
      {
        "id": "txn_001",
        "timestamp": "2025-11-22T22:15:00Z",
        "type": "earnings",
        "amount": 10,
        "source": "race",
        "details": {
          "position": 1,
          "race_id": "race_045"
        }
      },
      {
        "id": "txn_002",
        "timestamp": "2025-11-22T22:20:00Z",
        "type": "purchase",
        "amount": -150,
        "source": "shop",
        "details": {
          "item": "turtle",
          "turtle_id": "turtle_007"
        }
      },
      {
        "id": "txn_003",
        "timestamp": "2025-11-22T22:25:00Z",
        "type": "earnings",
        "amount": 1,
        "source": "voting",
        "details": {
          "category": "shell_pattern",
          "design_id": "design_123"
        }
      }
    ]
  }
}
```

---

## 3. Gene Data Format

### 3.1 Complete Turtle Gene Structure
```json
{
  "turtle_id": "turtle_001",
  "name": "Speedy",
  "generation": 3,
  "created_timestamp": "2025-11-20T15:30:00Z",
  "parents": {
    "mother_id": "turtle_004",
    "father_id": "turtle_005"
  },
  "genetics": {
    "shell_pattern": {
      "value": "hex",
      "dominance": 0.85,
      "mutation_source": "inherited",
      "parent_contribution": {
        "mother": 0.6,
        "father": 0.4
      }
    },
    "shell_color": {
      "value": "#4A90E2",
      "dominance": 0.92,
      "mutation_source": "inherited",
      "parent_contribution": {
        "mother": 0.7,
        "father": 0.3
      }
    },
    "pattern_color": {
      "value": "#E74C3C",
      "dominance": 0.78,
      "mutation_source": "mutation",
      "mutation_details": {
        "type": "adaptive",
        "similarity_to_parents": 0.3
      }
    },
    "limb_shape": {
      "value": "flippers",
      "dominance": 0.88,
      "mutation_source": "inherited",
      "parent_contribution": {
        "mother": 0.5,
        "father": 0.5
      }
    },
    "limb_length": {
      "value": 1.2,
      "dominance": 0.75,
      "mutation_source": "inherited",
      "parent_contribution": {
        "mother": 0.4,
        "father": 0.6
      }
    },
    "head_size": {
      "value": 0.9,
      "dominance": 0.82,
      "mutation_source": "inherited",
      "parent_contribution": {
        "mother": 0.55,
        "father": 0.45
      }
    },
    "eye_color": {
      "value": "#2ECC71",
      "dominance": 0.90,
      "mutation_source": "inherited",
      "parent_contribution": {
        "mother": 0.65,
        "father": 0.35
      }
    },
    "skin_texture": {
      "value": "smooth",
      "dominance": 0.79,
      "mutation_source": "inherited",
      "parent_contribution": {
        "mother": 0.5,
        "father": 0.5
      }
    }
  },
  "stats": {
    "speed": 8.5,
    "energy": 7.2,
    "recovery": 6.8,
    "swim": 9.1,
    "climb": 5.4,
    "base_stats": {
      "speed": 7.0,
      "energy": 7.0,
      "recovery": 7.0,
      "swim": 7.0,
      "climb": 7.0
    },
    "genetic_modifiers": {
      "speed": 1.5,
      "energy": 0.2,
      "recovery": -0.2,
      "swim": 2.1,
      "climb": -1.6
    }
  },
  "performance": {
    "race_history": [
      {
        "race_id": "race_043",
        "timestamp": "2025-11-22T21:00:00Z",
        "position": 1,
        "earnings": 10,
        "terrain_performance": {
          "grass": 9.2,
          "water": 8.8,
          "rock": 6.1
        }
      }
    ],
    "total_races": 15,
    "wins": 8,
    "average_position": 2.1,
    "total_earnings": 125
  }
}
```

### 3.2 Gene Pool Data
```json
{
  "gene_pool": {
    "version": "2.2.0",
    "last_updated": "2025-11-22T23:00:00Z",
    "trait_frequencies": {
      "shell_pattern": {
        "hex": 0.35,
        "spots": 0.25,
        "stripes": 0.20,
        "rings": 0.20
      },
      "limb_shape": {
        "flippers": 0.40,
        "feet": 0.35,
        "fins": 0.25
      },
      "limb_length": {
        "mean": 1.0,
        "std_dev": 0.3,
        "min": 0.5,
        "max": 1.5
      }
    },
    "dominant_traits": {
      "shell_pattern": "hex",
      "limb_shape": "flippers",
      "pattern_color": "#E74C3C"
    },
    "mutation_rates": {
      "point_mutation": 0.05,
      "adaptive_mutation": 0.03,
      "pattern_mutation": 0.02
    }
  }
}
```

---

## 4. Gene Preference Data Format

### 4.1 Player Voting Preferences
```json
{
  "player_preferences": {
    "version": "2.2.0",
    "player_id": "player_12345",
    "last_updated": "2025-11-22T23:09:00Z",
    "voting_history": [
      {
        "date": "2025-11-22",
        "design_id": "design_123",
        "ratings": {
          "shell_pattern": 5,
          "shell_color": 4,
          "pattern_color": 5,
          "limb_shape": 3,
          "limb_length": 4,
          "head_size": 3,
          "eye_color": 4,
          "skin_texture": 3
        },
        "rewards_earned": 8,
        "time_spent_minutes": 5
      }
    ],
    "preference_profile": {
      "trait_weights": {
        "shell_pattern": 0.25,
        "shell_color": 0.20,
        "pattern_color": 0.25,
        "limb_shape": 0.10,
        "limb_length": 0.10,
        "head_size": 0.05,
        "eye_color": 0.03,
        "skin_texture": 0.02
      },
      "color_preferences": {
        "favorite_colors": ["#4A90E2", "#E74C3C", "#2ECC71"],
        "avoided_colors": ["#95A5A6", "#34495E"],
        "color_harmony_score": 0.78
      },
      "pattern_preferences": {
        "favorite_patterns": ["hex", "spots"],
        "avoided_patterns": ["rings"],
        "complexity_preference": 0.6
      },
      "rating_behavior": {
        "average_rating": 4.2,
        "rating_variance": 0.8,
        "tendency_to_extreme": 0.15,
        "consistent_rater": true
      }
    },
    "genetic_influence": {
      "total_influence_points": 45,
      "trait_influence": {
        "shell_pattern": 12.5,
        "shell_color": 8.3,
        "pattern_color": 11.2,
        "limb_shape": 4.1,
        "limb_length": 4.8,
        "head_size": 2.0,
        "eye_color": 1.6,
        "skin_texture": 0.5
      },
      "influence_decay": {
        "daily_decay_rate": 0.05,
        "last_decay_date": "2025-11-22",
        "total_decayed": 2.3
      }
    }
  }
}
```

### 4.2 Community Preference Aggregates
```json
{
  "community_preferences": {
    "version": "2.2.0",
    "date": "2025-11-22",
    "total_voters": 156,
    "total_votes_cast": 1248,
    "trait_averages": {
      "shell_pattern": 3.8,
      "shell_color": 3.6,
      "pattern_color": 4.1,
      "limb_shape": 3.2,
      "limb_length": 3.4,
      "head_size": 2.9,
      "eye_color": 3.1,
      "skin_texture": 2.8
    },
    "popular_combinations": [
      {
        "combination": {
          "shell_pattern": "hex",
          "pattern_color": "#E74C3C",
          "limb_shape": "flippers"
        },
        "popularity_score": 0.78,
        "frequency": 0.23
      }
    ],
    "trending_traits": {
      "rising": ["hex", "flippers", "#E74C3C"],
      "declining": ["rings", "feet", "#95A5A6"],
      "stable": ["spots", "fins", "#2ECC71"]
    }
  }
}
```

---

## 5. Data Validation Schemas

### 5.1 Game Data Validation
```json
{
  "game_data_schema": {
    "type": "object",
    "required": ["version", "timestamp", "player_id", "game_state"],
    "properties": {
      "version": {
        "type": "string",
        "pattern": "^\\d+\\.\\d+\\.\\d+$"
      },
      "timestamp": {
        "type": "string",
        "format": "date-time"
      },
      "game_state": {
        "type": "object",
        "required": ["money", "current_phase"],
        "properties": {
          "money": {
            "type": "integer",
            "minimum": 0
          },
          "current_phase": {
            "type": "string",
            "enum": ["MENU", "ROSTER", "RACE", "SHOP", "BREEDING", "VOTING"]
          }
        }
      }
    }
  }
}
```

### 5.2 Gene Data Validation
```json
{
  "gene_data_schema": {
    "type": "object",
    "required": ["turtle_id", "genetics", "stats"],
    "properties": {
      "turtle_id": {
        "type": "string",
        "pattern": "^turtle_\\d{3}$"
      },
      "generation": {
        "type": "integer",
        "minimum": 0
      },
      "genetics": {
        "type": "object",
        "required": ["shell_pattern", "shell_color", "pattern_color"],
        "patternProperties": {
          "^(shell_pattern|shell_color|pattern_color|limb_shape|limb_length|head_size|eye_color|skin_texture)$": {
            "type": "object",
            "required": ["value", "dominance", "mutation_source"],
            "properties": {
              "value": {},
              "dominance": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0
              },
              "mutation_source": {
                "type": "string",
                "enum": ["inherited", "mutation", "random"]
              }
            }
          }
        }
      }
    }
  }
}
```

---

## 6. Performance Optimization

### 6.1 Data Compression
```json
{
  "compression_settings": {
    "enabled": true,
    "algorithm": "gzip",
    "level": 6,
    "target_size_reduction": 0.7,
    "compression_exceptions": [
      "game_state.session_stats",
      "turtle.performance.race_history"
    ]
  }
}
```

### 6.2 Incremental Updates
```json
{
  "incremental_update_format": {
    "base_version": "2.2.0",
    "update_timestamp": "2025-11-22T23:09:00Z",
    "changes": [
      {
        "path": "game_state.money",
        "operation": "add",
        "value": 5
      },
      {
        "path": "roster.active_turtles",
        "operation": "remove",
        "value": "turtle_003"
      }
    ]
  }
}
```

---

## 7. Migration Strategies

### 7.1 Version Migration
```json
{
  "migration_rules": {
    "2.1.0_to_2.2.0": {
      "field_renames": {
        "turtle.stats.speed_rating": "turtle.stats.speed"
      },
      "field_additions": {
        "turtle.genetics.skin_texture": {
          "default_value": "smooth",
          "dominance": 0.5,
          "mutation_source": "random"
        }
      },
      "data_transformations": {
        "game_state.money": {
          "operation": "multiply",
          "factor": 1.0
        }
      }
    }
  }
}
```

### 7.2 Backward Compatibility
```json
{
  "compatibility_matrix": {
    "2.2.0": {
      "can_load": ["2.1.0", "2.0.0"],
      "migration_required": ["2.1.0"],
      "deprecated_fields": {
        "turtle.stats.speed_rating": "Replaced with turtle.stats.speed"
      }
    }
  }
}
```

---

## 8. Security Considerations

### 8.1 Data Integrity
```json
{
  "integrity_checks": {
    "checksum_algorithm": "SHA-256",
    "signed_fields": [
      "game_state.money",
      "turtle.genetics",
      "player_preferences.genetic_influence"
    ],
    "tamper_detection": {
      "enabled": true,
      "action_on_tamper": "load_backup_or_reset"
    }
  }
}
```

### 8.2 Privacy Protection
```json
{
  "privacy_settings": {
    "anonymous_mode": false,
    "data_retention": {
      "race_history_days": 365,
      "transaction_history_days": 180
    },
    "sensitive_fields": [
      "player_id",
      "session_stats",
      "transaction_history"
    ]
  }
}
```

---

## 9. Implementation Guidelines

### 9.1 Data Access Patterns
```python
# Recommended access patterns
class GameDataManager:
    def get_turtle(self, turtle_id: str) -> TurtleData:
        # Direct access by turtle_id
        pass
    
    def get_gene_pool(self) -> GenePoolData:
        # Singleton access to gene pool
        pass
    
    def update_preferences(self, preferences: PreferenceData):
        # Atomic preference updates
        pass
    
    def get_performance_stats(self, turtle_id: str) -> PerformanceStats:
        # Aggregated performance data
        pass
```

### 9.2 Caching Strategy
```python
# Cache frequently accessed data
class DataCache:
    def __init__(self):
        self.turtle_cache = LRUCache(maxsize=100)
        self.gene_pool_cache = None  # Singleton
        self.preference_cache = LRUCache(maxsize=50)
    
    def get_turtle(self, turtle_id: str) -> TurtleData:
        if turtle_id not in self.turtle_cache:
            self.turtle_cache[turtle_id] = self.load_turtle(turtle_id)
        return self.turtle_cache[turtle_id]
```

---

## 10. Testing Data Formats

### 10.1 Test Data Templates
```json
{
  "test_templates": {
    "minimal_turtle": {
      "turtle_id": "test_001",
      "genetics": {
        "shell_pattern": {"value": "hex", "dominance": 1.0},
        "shell_color": {"value": "#4A90E2", "dominance": 1.0}
      },
      "stats": {"speed": 7.0, "energy": 7.0}
    },
    "complete_game_state": {
      "version": "2.2.0",
      "game_state": {
        "money": 1000,
        "current_phase": "ROSTER"
      },
      "roster": {
        "active_turtles": ["test_001"],
        "retired_turtles": []
      }
    }
  }
}
```

### 10.2 Validation Tests
```python
def test_gene_data_validation():
    # Test valid gene data
    valid_data = load_test_template("minimal_turtle")
    assert validate_gene_data(valid_data) == True
    
    # Test invalid gene data
    invalid_data = valid_data.copy()
    invalid_data["genetics"]["shell_pattern"]["dominance"] = 1.5
    assert validate_gene_data(invalid_data) == False

def test_migration_compatibility():
    # Test data migration from older versions
    old_data = load_version("2.1.0")
    new_data = migrate_data(old_data, "2.2.0")
    assert validate_gene_data(new_data) == True
```

---

## 11. Conclusion

The data formats defined in this document provide a comprehensive foundation for storing Game Data, Gene Data, and Gene Preference data in TurboShells. The formats are designed for:

- **Performance**: Optimized JSON structure with compression support
- **Reliability**: Built-in validation and integrity checks
- **Extensibility**: Version compatibility and migration strategies
- **Security**: Data integrity protection and privacy considerations

**Next Steps:**
1. Implement data validation schemas
2. Create data migration utilities
3. Set up automated testing for data formats
4. Integrate with save system implementation

---

*This document will be updated as the data requirements evolve and new features are added.*
