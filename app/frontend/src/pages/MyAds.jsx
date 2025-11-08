import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { Badge } from "../components/ui/badge";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "../components/ui/alert-dialog";
import {
  Plus,
  Edit,
  Trash2,
  ExternalLink,
  Search,
  Filter,
  Eye,
  MessageSquare,
  DollarSign,
  Loader2,
  PackageOpen,
} from "lucide-react";
import { api } from "../lib/api";

const MyAds = () => {
  const navigate = useNavigate();
  const [ads, setAds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [platformFilter, setPlatformFilter] = useState("all");
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    fetchAds();
  }, [statusFilter, platformFilter]);

  const fetchAds = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (statusFilter !== "all") params.append("status", statusFilter);
      if (platformFilter !== "all") params.append("platform", platformFilter);

      const data = await api.get(`/api/ads/?${params.toString()}`);
      setAds(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error fetching ads:", err);
      setError(err.message || "Failed to load ads");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (adId) => {
    try {
      setDeletingId(adId);
      await api.delete(`/api/ads/${adId}`);
      setAds(prev => prev.filter(ad => ad.id !== adId));
    } catch (err) {
      console.error("Error deleting ad:", err);
      alert("Failed to delete ad: " + err.message);
    } finally {
      setDeletingId(null);
    }
  };

  const handlePostToPlatforms = async (adId) => {
    navigate(`/marketplace/edit-ad/${adId}?action=post`);
  };

  const filteredAds = ads.filter(ad => {
    if (!searchQuery) return true;
    return ad.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
           ad.description?.toLowerCase().includes(searchQuery.toLowerCase());
  });

  const getStatusColor = (status) => {
    const colors = {
      draft: "bg-gray-100 text-gray-800",
      active: "bg-green-100 text-green-800",
      posted: "bg-blue-100 text-blue-800",
      paused: "bg-yellow-100 text-yellow-800",
      sold: "bg-purple-100 text-purple-800",
      expired: "bg-red-100 text-red-800",
    };
    return colors[status] || colors.draft;
  };

  const getPlatformIcon = (platform) => {
    const icons = {
      facebook: "📘",
      ebay: "🛒",
      offerup: "📱",
      craigslist: "📝",
    };
    return icons[platform] || "📦";
  };

  if (loading) {
    return (
      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex items-center justify-between">
          <h2 className="text-3xl font-bold tracking-tight">My Ads</h2>
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
        <h2 className="text-3xl font-bold tracking-tight">My Ads</h2>
        <Link to="/marketplace/create-ad">
          <Button className="bg-blue-600 hover:bg-blue-700">
            <Plus className="mr-2 h-4 w-4" />
            Create New Ad
          </Button>
        </Link>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <span className="text-red-600 font-medium">{error}</span>
              <Button onClick={fetchAds} variant="outline" size="sm">
                Retry
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Filter & Search</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search ads..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>

            {/* Status Filter */}
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger>
                <Filter className="mr-2 h-4 w-4" />
                <SelectValue placeholder="All Statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="posted">Posted</SelectItem>
                <SelectItem value="paused">Paused</SelectItem>
                <SelectItem value="sold">Sold</SelectItem>
              </SelectContent>
            </Select>

            {/* Platform Filter */}
            <Select value={platformFilter} onValueChange={setPlatformFilter}>
              <SelectTrigger>
                <SelectValue placeholder="All Platforms" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Platforms</SelectItem>
                <SelectItem value="facebook">Facebook</SelectItem>
                <SelectItem value="ebay">eBay</SelectItem>
                <SelectItem value="offerup">OfferUp</SelectItem>
                <SelectItem value="craigslist">Craigslist</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Ads List */}
      {filteredAds.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <PackageOpen className="mx-auto h-16 w-16 text-gray-400 mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {searchQuery || statusFilter !== "all" || platformFilter !== "all"
                  ? "No ads match your filters"
                  : "No ads yet"}
              </h3>
              <p className="text-gray-600 mb-6">
                {searchQuery || statusFilter !== "all" || platformFilter !== "all"
                  ? "Try adjusting your filters to see more results"
                  : "Create your first ad to start selling on multiple platforms"}
              </p>
              {!searchQuery && statusFilter === "all" && platformFilter === "all" && (
                <Link to="/marketplace/create-ad">
                  <Button className="bg-blue-600 hover:bg-blue-700">
                    <Plus className="mr-2 h-4 w-4" />
                    Create Your First Ad
                  </Button>
                </Link>
              )}
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {filteredAds.map((ad) => (
            <Card key={ad.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between gap-4">
                  {/* Ad Image */}
                  <div className="flex-shrink-0">
                    {ad.images && ad.images.length > 0 ? (
                      <img
                        src={ad.images[0]}
                        alt={ad.title}
                        className="w-24 h-24 object-cover rounded-lg"
                        onError={(e) => {
                          e.target.src = "https://via.placeholder.com/96";
                        }}
                      />
                    ) : (
                      <div className="w-24 h-24 bg-gray-200 rounded-lg flex items-center justify-center">
                        <PackageOpen className="h-8 w-8 text-gray-400" />
                      </div>
                    )}
                  </div>

                  {/* Ad Details */}
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-1">
                          {ad.title}
                        </h3>
                        <p className="text-gray-600 line-clamp-2">
                          {ad.description}
                        </p>
                      </div>
                      <Badge className={getStatusColor(ad.status)}>
                        {ad.status}
                      </Badge>
                    </div>

                    {/* Platforms */}
                    {ad.platforms && ad.platforms.length > 0 && (
                      <div className="flex items-center gap-2 mb-3">
                        <span className="text-sm text-gray-600">Posted on:</span>
                        {ad.platforms.map((platform) => (
                          <span
                            key={platform}
                            className="text-lg"
                            title={platform}
                          >
                            {getPlatformIcon(platform)}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Stats */}
                    <div className="flex items-center gap-6 text-sm text-gray-600 mb-4">
                      <div className="flex items-center gap-1">
                        <DollarSign className="h-4 w-4" />
                        <span className="font-semibold text-blue-600">
                          ${ad.price?.toFixed(2)}
                        </span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Eye className="h-4 w-4" />
                        <span>{ad.views || 0} views</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <MessageSquare className="h-4 w-4" />
                        <span>{ad.leads || 0} leads</span>
                      </div>
                      {ad.category && (
                        <span className="text-gray-500">• {ad.category}</span>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2">
                      <Link to={`/marketplace/edit-ad/${ad.id}`}>
                        <Button variant="outline" size="sm">
                          <Edit className="mr-2 h-4 w-4" />
                          Edit
                        </Button>
                      </Link>

                      {ad.status === "draft" && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handlePostToPlatforms(ad.id)}
                        >
                          <ExternalLink className="mr-2 h-4 w-4" />
                          Post to Platforms
                        </Button>
                      )}

                      <Link to={`/marketplace/analytics?ad=${ad.id}`}>
                        <Button variant="outline" size="sm">
                          <Eye className="mr-2 h-4 w-4" />
                          Analytics
                        </Button>
                      </Link>

                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button
                            variant="outline"
                            size="sm"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            disabled={deletingId === ad.id}
                          >
                            {deletingId === ad.id ? (
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            ) : (
                              <Trash2 className="mr-2 h-4 w-4" />
                            )}
                            Delete
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>
                              Are you sure you want to delete this ad?
                            </AlertDialogTitle>
                            <AlertDialogDescription>
                              This action cannot be undone. This will permanently
                              delete your ad "{ad.title}" and remove it from all
                              platforms.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                            <AlertDialogAction
                              onClick={() => handleDelete(ad.id)}
                              className="bg-red-600 hover:bg-red-700"
                            >
                              Delete
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Summary Stats */}
      {filteredAds.length > 0 && (
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>
                Showing {filteredAds.length} of {ads.length} ads
              </span>
              <div className="flex items-center gap-4">
                <span>
                  Total Value: ${filteredAds.reduce((sum, ad) => sum + (ad.price || 0), 0).toFixed(2)}
                </span>
                <span>
                  Total Views: {filteredAds.reduce((sum, ad) => sum + (ad.views || 0), 0)}
                </span>
                <span>
                  Total Leads: {filteredAds.reduce((sum, ad) => sum + (ad.leads || 0), 0)}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default MyAds;
