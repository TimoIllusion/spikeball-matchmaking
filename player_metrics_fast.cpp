#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <string>
#include <cmath>
#include <numeric>
#include <algorithm>

namespace py = pybind11;

// Helper function to find consecutive numbers
std::vector<int> find_consecutive_numbers(const std::vector<int>& arr, int target_number) {
    std::vector<int> lengths;
    int length = 0;
    
    for (int num : arr) {
        if (num == target_number) {
            length++;
        } else {
            if (length > 0) {
                lengths.push_back(length);
            }
            length = 0;
        }
    }
    
    if (length > 0) {
        lengths.push_back(length);
    }
    
    return lengths;
}

// Helper function to count consecutive occurrences
std::unordered_map<std::string, int> count_consecutive_occurrences(const std::vector<std::string>& symbols) {
    std::unordered_map<std::string, int> counter;
    int temp_counter = 0;
    
    for (size_t i = 1; i < symbols.size(); i++) {
        if (symbols[i] == symbols[i-1]) {
            temp_counter++;
        } else {
            counter[symbols[i-1]] += temp_counter;
            temp_counter = 0;
        }
    }
    
    return counter;
}

// Calculate standard deviation
double calculate_stdev(const std::vector<double>& values) {
    if (values.empty()) return 0.0;
    
    double mean = std::accumulate(values.begin(), values.end(), 0.0) / values.size();
    double sq_sum = 0.0;
    
    for (double val : values) {
        sq_sum += (val - mean) * (val - mean);
    }
    
    return std::sqrt(sq_sum / values.size());
}

double calculate_stdev(const std::vector<int>& values) {
    if (values.empty()) return 0.0;
    
    double mean = std::accumulate(values.begin(), values.end(), 0.0) / values.size();
    double sq_sum = 0.0;
    
    for (int val : values) {
        sq_sum += (val - mean) * (val - mean);
    }
    
    return std::sqrt(sq_sum / values.size());
}

struct PlayerStatistics {
    int num_played_matches;
    std::vector<int> break_lengths;
    double break_lengths_avg;
    double break_lengths_stdev;
    std::unordered_map<int, int> break_lengths_hist;
    double matchup_lengths_played_between_breaks_second_session_only;
    std::vector<int> matchup_lengths_played_between_breaks;
    std::unordered_map<std::string, int> teammate_hist;
    double teammate_hist_stdev;
    std::unordered_map<std::string, int> enemy_teams_hist;
    double enemy_teams_hist_stdev;
    std::unordered_map<std::string, int> consecutive_teammates_hist;
    std::unordered_map<std::string, int> consecutive_enemies_hist;
    int consecutive_teammates_total;
    int consecutive_enemies_total;
    int num_unique_people_not_played_with_or_against;
    int num_unique_people_not_played_with;
    int num_unique_people_not_played_against;
};

// Simple matchup data structure
struct MatchupData {
    std::vector<std::string> all_player_uids;
    std::unordered_map<std::string, std::string> player_to_teammate;
    std::unordered_map<std::string, std::string> player_to_enemy_team;
    std::unordered_map<std::string, std::vector<std::string>> player_to_enemy_players;
};

class PlayerMetricCalculatorCpp {
private:
    std::vector<MatchupData> matchups;
    int num_players;
    std::string player_uid;
    int num_fields;
    
    // Cached data
    std::vector<int> played_matches;
    std::vector<int> break_lengths;
    std::vector<int> matchup_lengths_played_between_breaks;
    std::vector<std::string> teammate_uids;
    std::unordered_map<std::string, int> teammate_hist;
    std::unordered_map<std::string, int> consecutive_teammates_hist;
    std::vector<std::string> enemy_team_uids;
    std::vector<std::string> enemy_player_uids;
    std::unordered_map<std::string, int> enemy_teams_hist;
    std::unordered_map<std::string, int> consecutive_enemies_hist;

public:
    PlayerMetricCalculatorCpp(const std::vector<MatchupData>& matchups_data, 
                             int num_players, 
                             const std::string& player_uid, 
                             int num_fields)
        : matchups(matchups_data), num_players(num_players), player_uid(player_uid), num_fields(num_fields) {
        calculate_base_statistics();
    }
    
    void calculate_base_statistics() {
        played_matches = get_played_matches();
        break_lengths = find_consecutive_numbers(played_matches, 0);
        matchup_lengths_played_between_breaks = find_consecutive_numbers(played_matches, 1);
        
        // Get teammate UIDs
        for (const auto& matchup : matchups) {
            auto it = std::find(matchup.all_player_uids.begin(), matchup.all_player_uids.end(), player_uid);
            if (it != matchup.all_player_uids.end()) {
                auto teammate_it = matchup.player_to_teammate.find(player_uid);
                if (teammate_it != matchup.player_to_teammate.end()) {
                    teammate_uids.push_back(teammate_it->second);
                }
            }
        }
        
        // Calculate teammate histogram
        for (const auto& teammate : teammate_uids) {
            teammate_hist[teammate]++;
        }
        
        consecutive_teammates_hist = count_consecutive_occurrences(teammate_uids);
        
        // Get enemy team UIDs and player UIDs
        for (const auto& matchup : matchups) {
            auto it = std::find(matchup.all_player_uids.begin(), matchup.all_player_uids.end(), player_uid);
            if (it != matchup.all_player_uids.end()) {
                auto enemy_team_it = matchup.player_to_enemy_team.find(player_uid);
                if (enemy_team_it != matchup.player_to_enemy_team.end()) {
                    enemy_team_uids.push_back(enemy_team_it->second);
                }
                
                auto enemy_players_it = matchup.player_to_enemy_players.find(player_uid);
                if (enemy_players_it != matchup.player_to_enemy_players.end()) {
                    for (const auto& enemy : enemy_players_it->second) {
                        enemy_player_uids.push_back(enemy);
                    }
                }
            }
        }
        
        // Calculate enemy teams histogram
        for (const auto& enemy_team : enemy_team_uids) {
            enemy_teams_hist[enemy_team]++;
        }
        
        consecutive_enemies_hist = count_consecutive_occurrences(enemy_team_uids);
    }
    
    std::vector<int> get_played_matches() {
        std::vector<bool> played_matches_bool;
        played_matches_bool.reserve(matchups.size());
        
        for (const auto& matchup : matchups) {
            bool found = std::find(matchup.all_player_uids.begin(), matchup.all_player_uids.end(), player_uid) 
                        != matchup.all_player_uids.end();
            played_matches_bool.push_back(found);
        }
        
        // Reshape into rounds with num_fields columns and check if player played on ANY field
        std::vector<int> played_matches_per_round;
        for (size_t i = 0; i < played_matches_bool.size(); i += num_fields) {
            bool played_in_round = false;
            for (int j = 0; j < num_fields && (i + j) < played_matches_bool.size(); j++) {
                if (played_matches_bool[i + j]) {
                    played_in_round = true;
                    break;
                }
            }
            played_matches_per_round.push_back(played_in_round ? 1 : 0);
        }
        
        return played_matches_per_round;
    }
    
    PlayerStatistics calculate_player_stats() {
        PlayerStatistics stats;
        
        // Basic counts
        stats.num_played_matches = std::accumulate(played_matches.begin(), played_matches.end(), 0);
        stats.break_lengths = break_lengths;
        
        // Break statistics
        if (!break_lengths.empty()) {
            stats.break_lengths_avg = std::accumulate(break_lengths.begin(), break_lengths.end(), 0.0) / break_lengths.size();
            stats.break_lengths_stdev = calculate_stdev(break_lengths);
        } else {
            stats.break_lengths_avg = 0.0;
            stats.break_lengths_stdev = 0.0;
        }
        
        // Break lengths histogram
        for (int length : break_lengths) {
            stats.break_lengths_hist[length]++;
        }
        
        // Matchup lengths between breaks
        stats.matchup_lengths_played_between_breaks = matchup_lengths_played_between_breaks;
        stats.matchup_lengths_played_between_breaks_second_session_only = 
            (matchup_lengths_played_between_breaks.size() > 1) ? 
            matchup_lengths_played_between_breaks[1] : 10.0;
        
        // Teammate statistics
        stats.teammate_hist = teammate_hist;
        std::vector<int> teammate_hist_values;
        for (const auto& pair : teammate_hist) {
            teammate_hist_values.push_back(pair.second);
        }
        stats.teammate_hist_stdev = calculate_stdev(teammate_hist_values);
        
        // Enemy team statistics
        stats.enemy_teams_hist = enemy_teams_hist;
        std::vector<int> enemy_teams_hist_values;
        for (const auto& pair : enemy_teams_hist) {
            enemy_teams_hist_values.push_back(pair.second);
        }
        stats.enemy_teams_hist_stdev = calculate_stdev(enemy_teams_hist_values);
        
        // Consecutive statistics
        stats.consecutive_teammates_hist = consecutive_teammates_hist;
        stats.consecutive_enemies_hist = consecutive_enemies_hist;
        
        stats.consecutive_teammates_total = 0;
        for (const auto& pair : consecutive_teammates_hist) {
            stats.consecutive_teammates_total += pair.second;
        }
        
        stats.consecutive_enemies_total = 0;
        for (const auto& pair : consecutive_enemies_hist) {
            stats.consecutive_enemies_total += pair.second;
        }
        
        // Unique people statistics
        std::unordered_set<std::string> all_played_with_or_against;
        std::unordered_set<std::string> all_played_with(teammate_uids.begin(), teammate_uids.end());
        std::unordered_set<std::string> all_played_against(enemy_player_uids.begin(), enemy_player_uids.end());
        
        all_played_with_or_against.insert(teammate_uids.begin(), teammate_uids.end());
        all_played_with_or_against.insert(enemy_player_uids.begin(), enemy_player_uids.end());
        
        stats.num_unique_people_not_played_with_or_against = (num_players - 1) - all_played_with_or_against.size();
        stats.num_unique_people_not_played_with = (num_players - 1) - all_played_with.size();
        stats.num_unique_people_not_played_against = (num_players - 1) - all_played_against.size();
        
        return stats;
    }
};

class GlobalMetricCalculatorCpp {
private:
    std::unordered_map<std::string, PlayerStatistics> player_stats;
    int num_players;

public:
    GlobalMetricCalculatorCpp(const std::unordered_map<std::string, PlayerStatistics>& stats, int num_players)
        : player_stats(stats), num_players(num_players) {}
    
    int compute_not_playing_players_index() {
        return num_players - player_stats.size();
    }
    
    double compute_played_matches_index() {
        std::vector<int> global_num_played_matches;
        for (const auto& pair : player_stats) {
            global_num_played_matches.push_back(pair.second.num_played_matches);
        }
        return calculate_stdev(global_num_played_matches);
    }
    
    double compute_break_shortness_index() {
        std::vector<int> global_player_break_lengths;
        for (const auto& pair : player_stats) {
            for (int length : pair.second.break_lengths) {
                global_player_break_lengths.push_back(length);
            }
        }
        
        // Filter out breaks of length 1 and square them
        double sum_squared = 0.0;
        for (int length : global_player_break_lengths) {
            if (length > 1) {
                sum_squared += length * length;
            }
        }
        
        return sum_squared;
    }
    
    double compute_second_continuous_matchup_length_focused_on_short_sessions_index() {
        std::vector<double> per_player_values;
        for (const auto& pair : player_stats) {
            per_player_values.push_back(pair.second.matchup_lengths_played_between_breaks_second_session_only);
        }
        return calculate_stdev(per_player_values);
    }
    
    double compute_teammate_variety_index() {
        double sum = 0.0;
        for (const auto& pair : player_stats) {
            sum += pair.second.teammate_hist_stdev;
        }
        return sum;
    }
    
    double compute_enemy_team_variety_index() {
        double sum = 0.0;
        for (const auto& pair : player_stats) {
            sum += pair.second.enemy_teams_hist_stdev;
        }
        return sum;
    }
    
    double compute_teammate_succession_index() {
        int sum = 0;
        for (const auto& pair : player_stats) {
            sum += pair.second.consecutive_teammates_total;
        }
        return static_cast<double>(sum);
    }
    
    double compute_enemy_team_succession_index() {
        int sum = 0;
        for (const auto& pair : player_stats) {
            sum += pair.second.consecutive_enemies_total;
        }
        return static_cast<double>(sum);
    }
    
    double compute_player_engagement_fairness_index() {
        std::vector<int> per_player_values;
        for (const auto& pair : player_stats) {
            per_player_values.push_back(pair.second.num_unique_people_not_played_with_or_against);
        }
        return calculate_stdev(per_player_values);
    }
    
    double compute_not_played_with_or_against_players_index() {
        int sum = 0;
        for (const auto& pair : player_stats) {
            sum += pair.second.num_unique_people_not_played_with_or_against;
        }
        return static_cast<double>(sum);
    }
    
    double compute_not_played_with_players_index() {
        int sum = 0;
        for (const auto& pair : player_stats) {
            sum += pair.second.num_unique_people_not_played_with;
        }
        return static_cast<double>(sum);
    }
    
    double compute_not_played_against_players_index() {
        int sum = 0;
        for (const auto& pair : player_stats) {
            sum += pair.second.num_unique_people_not_played_against;
        }
        return static_cast<double>(sum);
    }
    
    std::unordered_map<std::string, double> calculate_global_stats() {
        return {
            {"global_not_playing_players_index", static_cast<double>(compute_not_playing_players_index())},
            {"global_played_matches_index", compute_played_matches_index()},
            {"global_matchup_session_length_between_breaks_index", compute_second_continuous_matchup_length_focused_on_short_sessions_index()},
            {"global_break_shortness_index", compute_break_shortness_index()},
            {"global_teammate_variety_index", compute_teammate_variety_index()},
            {"global_enemy_team_variety_index", compute_enemy_team_variety_index()},
            {"global_teammate_succession_index", compute_teammate_succession_index()},
            {"global_enemy_team_succession_index", compute_enemy_team_succession_index()},
            {"global_player_engagement_fairness_index", compute_player_engagement_fairness_index()},
            {"global_not_played_with_or_against_players_index", compute_not_played_with_or_against_players_index()},
            {"global_not_played_with_players_index", compute_not_played_with_players_index()},
            {"global_not_played_against_players_index", compute_not_played_against_players_index()}
        };
    }
};

// Main function to calculate all statistics
std::pair<std::unordered_map<std::string, double>, double> 
get_total_matchup_set_score_cpp(const std::vector<MatchupData>& matchups,
                               int num_players,
                               const std::unordered_map<std::string, double>& weights,
                               int num_fields) {
    
    // Get unique players
    std::unordered_set<std::string> unique_players_set;
    for (const auto& matchup : matchups) {
        for (const auto& player_uid : matchup.all_player_uids) {
            unique_players_set.insert(player_uid);
        }
    }
    
    std::vector<std::string> unique_players(unique_players_set.begin(), unique_players_set.end());
    
    // Calculate all player statistics
    std::unordered_map<std::string, PlayerStatistics> results;
    for (const auto& player_uid : unique_players) {
        PlayerMetricCalculatorCpp calculator(matchups, num_players, player_uid, num_fields);
        results[player_uid] = calculator.calculate_player_stats();
    }
    
    // Calculate global metrics
    GlobalMetricCalculatorCpp global_calculator(results, num_players);
    auto global_results = global_calculator.calculate_global_stats();
    
    // Calculate weighted loss
    double loss = 0.0;
    for (const auto& pair : weights) {
        auto it = global_results.find(pair.first);
        if (it != global_results.end()) {
            loss += pair.second * it->second;
        }
    }
    
    return std::make_pair(global_results, loss);
}

PYBIND11_MODULE(matchmaking_fast, m) {
    m.doc() = "Fast C++ implementation of matchmaking metrics";
    
    py::class_<MatchupData>(m, "MatchupData")
        .def(py::init<>())
        .def_readwrite("all_player_uids", &MatchupData::all_player_uids)
        .def_readwrite("player_to_teammate", &MatchupData::player_to_teammate)
        .def_readwrite("player_to_enemy_team", &MatchupData::player_to_enemy_team)
        .def_readwrite("player_to_enemy_players", &MatchupData::player_to_enemy_players);
    
    py::class_<PlayerStatistics>(m, "PlayerStatistics")
        .def(py::init<>())
        .def_readwrite("num_played_matches", &PlayerStatistics::num_played_matches)
        .def_readwrite("break_lengths", &PlayerStatistics::break_lengths)
        .def_readwrite("break_lengths_avg", &PlayerStatistics::break_lengths_avg)
        .def_readwrite("break_lengths_stdev", &PlayerStatistics::break_lengths_stdev)
        .def_readwrite("teammate_hist_stdev", &PlayerStatistics::teammate_hist_stdev)
        .def_readwrite("enemy_teams_hist_stdev", &PlayerStatistics::enemy_teams_hist_stdev)
        .def_readwrite("consecutive_teammates_total", &PlayerStatistics::consecutive_teammates_total)
        .def_readwrite("consecutive_enemies_total", &PlayerStatistics::consecutive_enemies_total)
        .def_readwrite("num_unique_people_not_played_with_or_against", &PlayerStatistics::num_unique_people_not_played_with_or_against)
        .def_readwrite("num_unique_people_not_played_with", &PlayerStatistics::num_unique_people_not_played_with)
        .def_readwrite("num_unique_people_not_played_against", &PlayerStatistics::num_unique_people_not_played_against);
    
    py::class_<PlayerMetricCalculatorCpp>(m, "PlayerMetricCalculatorCpp")
        .def(py::init<const std::vector<MatchupData>&, int, const std::string&, int>())
        .def("calculate_player_stats", &PlayerMetricCalculatorCpp::calculate_player_stats);
    
    py::class_<GlobalMetricCalculatorCpp>(m, "GlobalMetricCalculatorCpp")
        .def(py::init<const std::unordered_map<std::string, PlayerStatistics>&, int>())
        .def("calculate_global_stats", &GlobalMetricCalculatorCpp::calculate_global_stats);
    
    m.def("get_total_matchup_set_score_cpp", &get_total_matchup_set_score_cpp, 
          "Calculate total matchup set score using C++");
    
    m.def("find_consecutive_numbers", &find_consecutive_numbers,
          "Find consecutive numbers in array");
}