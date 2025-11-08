import React, { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import {
  TrendingUp,
  TrendingDown,
  Eye,
  MessageSquare,
  DollarSign,
  Users,
  Calendar,
  Download,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { api } from "../lib/api";

const Analytics = () => {
  const [searchParams] = useSearchParams();
  const adId = searchParams.get("ad");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState("7d");
  const [analytics, setAnalytics] = useState(null);
  const [ads, setAds] = useState([]);
  const [selectedAd, setSelectedAd] = useState(adId || "all");

  useEffect(() => {
    fetchAds();
  }, []);

  useEffect(() => {
    if (selectedAd) {
      fetchAnalytics();
    }
  }, [selectedAd, timeRange]);

  const fetchAds = async () => {
    try {
      const data = await api.get("/api/ads/");
      setAds(Array.isArray(data) ? data : []);
      if (!adId && data.length > 0) {
        setSelectedAd("all");
      }
    } catch (err) {
      console.error("Error fetching ads:", err);
    }
  };

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);

      const endpoint =
        selectedAd === "all"
          ? `/api/analytics/overview?timeRange=${timeRange}`
          : `/api/analytics/${selectedAd}?timeRange=${timeRange}`;

      const data = await api.get(endpoint);
      setAnalytics(data);
    } catch (err) {
      console.error("Error fetching analytics:", err);
      setError(err.message || "Failed to load analytics");
    } finally {
      setLoading(false);
    }
  };

  const exportData = () => {
    if (!analytics) return;

    const csvData = [
      ["Metric", "Value"],
      ["Total Views", analytics.totalViews || 0],
      ["Total Leads", analytics.totalLeads || 0],
      ["Total Revenue", `$${analytics.totalRevenue || 0}`],
      ["Conversion Rate", `${analytics.conversionRate || 0}%`],
    ];

    const csv = csvData.map((row) => row.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `analytics-${selectedAd}-${timeRange}.csv`;
    a.click();
  };

  const COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444"];

  // Mock data structure (replace with real API data)
  const mockViewsData = [
    { date: "Mon", views: 45 },
    { date: "Tue", views: 52 },
    { date: "Wed", views: 38 },
    { date: "Thu", views: 67 },
    { date: "Fri", views: 78 },
    { date: "Sat", views: 91 },
    { date: "Sun", views: 85 },
  ];

  const mockPlatformData = [
    { name: "Facebook", value: 45, color: "#3B82F6" },
    { name: "eBay", value: 23, color: "#F59E0B" },
    { name: "OfferUp", value: 67, color: "#10B981" },
    { name: "Craigslist", value: 12, color: "#8B5CF6" },
  ];

  const mockLeadsData = [
    { date: "Mon", leads: 5 },
    { date: "Tue", leads: 8 },
    { date: "Wed", leads: 3 },
    { date: "Thu", leads: 12 },
    { date: "Fri", leads: 15 },
    { date: "Sat", leads: 18 },
    { date: "Sun", leads: 14 },
  ];

  if (loading && !analytics) {
    return (
      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex items-center justify-between">
          <h2 className="text-3xl font-bold tracking-tight">Analytics</h2>
        </div>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">Analytics</h2>
        <div className="flex gap-2">
          <Button variant="outline" onClick={exportData}>
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-5 w-5" />
              <span className="font-medium">{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <div className="flex gap-4">
        <Select value={selectedAd} onValueChange={setSelectedAd}>
          <SelectTrigger className="w-64">
            <SelectValue placeholder="Select ad" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Ads</SelectItem>
            {ads.map((ad) => (
              <SelectItem key={ad.id} value={ad.id}>
                {ad.title}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={timeRange} onValueChange={setTimeRange}>
          <SelectTrigger className="w-48">
            <Calendar className="mr-2 h-4 w-4" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7d">Last 7 Days</SelectItem>
            <SelectItem value="30d">Last 30 Days</SelectItem>
            <SelectItem value="90d">Last 90 Days</SelectItem>
            <SelectItem value="all">All Time</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Views</CardTitle>
            <Eye className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics?.totalViews || 147}
            </div>
            <p className="text-xs text-muted-foreground flex items-center mt-1">
              <TrendingUp className="h-3 w-3 text-green-600 mr-1" />
              <span className="text-green-600">+12.5%</span>
              <span className="ml-1">from last period</span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Leads</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics?.totalLeads || 15}
            </div>
            <p className="text-xs text-muted-foreground flex items-center mt-1">
              <TrendingUp className="h-3 w-3 text-green-600 mr-1" />
              <span className="text-green-600">+8.3%</span>
              <span className="ml-1">from last period</span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Conversion Rate
            </CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics?.conversionRate || 10.2}%
            </div>
            <p className="text-xs text-muted-foreground flex items-center mt-1">
              <TrendingDown className="h-3 w-3 text-red-600 mr-1" />
              <span className="text-red-600">-2.1%</span>
              <span className="ml-1">from last period</span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Revenue
            </CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${analytics?.totalRevenue?.toLocaleString() || "1,247"}
            </div>
            <p className="text-xs text-muted-foreground flex items-center mt-1">
              <TrendingUp className="h-3 w-3 text-green-600 mr-1" />
              <span className="text-green-600">+15.2%</span>
              <span className="ml-1">from last period</span>
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Views Over Time */}
        <Card>
          <CardHeader>
            <CardTitle>Views Over Time</CardTitle>
            <CardDescription>Daily view count for selected period</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analytics?.viewsData || mockViewsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="views"
                  stroke="#3B82F6"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Platform Performance */}
        <Card>
          <CardHeader>
            <CardTitle>Platform Performance</CardTitle>
            <CardDescription>Views by platform</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={analytics?.platformData || mockPlatformData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {(analytics?.platformData || mockPlatformData).map(
                    (entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={entry.color || COLORS[index % COLORS.length]}
                      />
                    )
                  )}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Leads Over Time */}
        <Card>
          <CardHeader>
            <CardTitle>Leads Over Time</CardTitle>
            <CardDescription>Daily lead generation</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics?.leadsData || mockLeadsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="leads" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Performance Summary */}
        <Card>
          <CardHeader>
            <CardTitle>Performance Summary</CardTitle>
            <CardDescription>Key insights and recommendations</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
              <TrendingUp className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <p className="font-medium text-blue-900">Peak Performance</p>
                <p className="text-sm text-blue-700">
                  Saturdays show 45% more views. Consider posting new items on
                  Fridays.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
              <Users className="h-5 w-5 text-green-600 mt-0.5" />
              <div>
                <p className="font-medium text-green-900">Best Platform</p>
                <p className="text-sm text-green-700">
                  OfferUp generates 67% of your views. Focus more content here.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3 bg-yellow-50 rounded-lg">
              <MessageSquare className="h-5 w-5 text-yellow-600 mt-0.5" />
              <div>
                <p className="font-medium text-yellow-900">Response Time</p>
                <p className="text-sm text-yellow-700">
                  Average response time: 2.5 hours. Faster responses increase
                  sales by 23%.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3 bg-purple-50 rounded-lg">
              <DollarSign className="h-5 w-5 text-purple-600 mt-0.5" />
              <div>
                <p className="font-medium text-purple-900">
                  Price Optimization
                </p>
                <p className="text-sm text-purple-700">
                  Items priced $5-10 below market average sell 2x faster.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Mermaid Diagram Visualization */}
      <Card>
        <CardHeader>
          <CardTitle>Ad Performance Flow</CardTitle>
          <CardDescription>
            Visual representation of your ad's journey
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-50 p-6 rounded-lg font-mono text-sm">
            <pre className="text-gray-700">
              {`graph TD
    A[Your Ad Posted] --> B{Posted to 4 Platforms}
    B --> C[Facebook: 45 views]
    B --> D[eBay: 23 views]
    B --> E[OfferUp: 67 views]
    B --> F[Craigslist: 12 views]

    C --> G[Total: 147 views]
    D --> G
    E --> G
    F --> G

    G --> H[15 Leads Generated]
    H --> I[3 Sales Completed]
    I --> J[$1,247 Revenue]`}
            </pre>
          </div>
          <p className="text-sm text-gray-600 mt-4">
            💡 <strong>Tip:</strong> This Mermaid diagram shows your conversion
            funnel. Copy this to visualize in any Mermaid-compatible tool.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default Analytics;
