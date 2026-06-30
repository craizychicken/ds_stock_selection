#include <iostream>
#include <vector>
#include <map>

struct BacktestInput{
    std::vector<std::string> dates; // Date format 'yyy-mm-dd'
    std::vector<std::string> rebalancing_dates;
    std::map<std::string, std::vector<double>> prices; // symbol -> close prices (sorted by date)
    std::map<std::string, std::map<std::string, double>> weights; // rebalancing -> <symbol -> weight>
    std::map<std::string, std::vector<std::vector<double>>> signal; // <z_reversion, close location> sorted by date
    double capital;
    double transaction_cost;
    double stop_loss;
};

struct DailySnapshot{
    std::string date;
    double portfolio_value;
    double cash; // Date format 'yyy-mm-dd'
    double daily_return;
};

