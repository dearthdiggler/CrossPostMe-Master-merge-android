import React, { useState, useEffect } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Label } from "../components/ui/label";
import { Checkbox } from "../components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../components/ui/alert-dialog";
import {
  Save,
  Sparkles,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Plus,
  Trash2,
  Send
} from "lucide-react";
import { api } from "../lib/api";

const EditAd = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const shouldPost = searchParams.get('action') === 'post';

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [posting, setPosting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [showPostDialog, setShowPostDialog] = useState(shouldPost);
  const [selectedPlatformsToPost, setSelectedPlatformsToPost] = useState([]);

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    price: "",
    category: "",
    location: "",
    images: [],
    platforms: [],
    status: "draft",
  });

  const categories = [
    "Electronics",
    "Furniture",
    "Vehicles",
    "Real Estate",
    "Appliances",
    "Clothing",
    "Sports",
    "Tools",
    "Other"
  ];

  const platforms = [
    { id: "facebook", name: "Facebook Marketplace", icon: "📘" },
    { id: "ebay", name: "eBay", icon: "🛒" },
    { id: "offerup", name: "OfferUp", icon: "📱" },
    { id: "craigslist", name: "Craigslist", icon: "📝" },
  ];

  useEffect(() => {
    fetchAd();
  }, [id]);

  const fetchAd = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.get(`/api/ads/${id}`);
      setFormData({
        ...data,
        price: data.price?.toString() || "",
        platforms: data.platforms || [],
      });
    } catch (err) {
      console.error("Error fetching ad:", err);
      setError(err.message || "Failed to load ad");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePlatformToggle = (platformId) => {
    setFormData(prev => ({
      ...prev,
      platforms: prev.platforms.includes(platformId)
        ? prev.platforms.filter(p => p !== platformId)
        : [...prev.platforms, platformId]
    }));
  };

  const handleImageAdd = () => {
    const url = prompt("Enter image URL:");
    if (url) {
      setFormData(prev => ({
        ...prev,
        images: [...prev.images, url]
      }));
    }
  };

  const handleImageRemove = (index) => {
    setFormData(prev => ({
      ...prev,
      images: prev.images.filter((_, i) => i !== index)
    }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    if (!formData.title || !formData.description || !formData.price) {
      setError("Please fill in all required fields");
      return;
    }

    try {
      setSaving(true);

      const updateData = {
        title: formData.title,
        description: formData.description,
        price: parseFloat(formData.price),
        category: formData.category,
        location: formData.location,
        images: formData.images,
        platforms: formData.platforms,
        status: formData.status,
      };

      await api.put(`/api/ads/${id}`, updateData);

      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
      }, 3000);

    } catch (err) {
      console.error("Error updating ad:", err);
      setError(err.message || "Failed to update ad. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const handlePostToPlatforms = async () => {
    if (selectedPlatformsToPost.length === 0) {
      alert("Please select at least one platform");
      return;
    }

    try {
      setPosting(true);
      setError(null);

      const response = await api.post(`/api/ads/${id}/post-multiple`, {
        platforms: selectedPlatformsToPost
      });

      setShowPostDialog(false);
      setSuccess(true);

      setTimeout(() => {
        navigate("/marketplace/my-ads");
      }, 2000);

    } catch (err) {
      console.error("Error posting ad:", err);
      setError(err.message || "Failed to post ad to platforms");
    } finally {
      setPosting(false);
    }
  };

  const handleAIGenerate = async () => {
    if (!formData.title) {
      alert("Please enter a title first");
      return;
    }

    try {
      setSaving(true);
      const response = await api.post("/api/listing-assistant/generate", {
        keywords: formData.title.split(" "),
        category: formData.category || "General",
        platforms: formData.platforms.length > 0 ? formData.platforms : ["facebook"]
      });

      if (response.content) {
        setFormData(prev => ({
          ...prev,
          description: response.content
        }));
      }
    } catch (err) {
      console.error("AI generation failed:", err);
      alert("AI generation failed. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex items-center justify-between">
          <h2 className="text-3xl font-bold tracking-tight">Edit Ad</h2>
        </div>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
        </div>
      </div>
    );
  }

  if (error && !formData.title) {
    return (
      <div className="flex-1 space-y-4 p-8 pt-6">
        <h2 className="text-3xl font-bold tracking-tight">Edit Ad</h2>
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-5 w-5" />
              <span className="font-medium">{error}</span>
            </div>
            <Button
              onClick={() => navigate("/marketplace/my-ads")}
              className="mt-4"
              variant="outline"
            >
              Back to My Ads
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">Edit Ad</h2>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => navigate("/marketplace/my-ads")}
          >
            Cancel
          </Button>
          <Button
            onClick={() => setShowPostDialog(true)}
            className="bg-green-600 hover:bg-green-700"
            disabled={formData.status === "draft"}
          >
            <Send className="mr-2 h-4 w-4" />
            Post to Platforms
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

      {success && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-green-600">
              <CheckCircle2 className="h-5 w-5" />
              <span className="font-medium">Ad updated successfully!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Ad Details</CardTitle>
            <CardDescription>
              Update your ad information
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Title */}
            <div className="space-y-2">
              <Label htmlFor="title">
                Title <span className="text-red-500">*</span>
              </Label>
              <Input
                id="title"
                name="title"
                placeholder="e.g., iPhone 13 Pro Max - Unlocked"
                value={formData.title}
                onChange={handleInputChange}
                required
              />
            </div>

            {/* Description */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="description">
                  Description <span className="text-red-500">*</span>
                </Label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleAIGenerate}
                  disabled={saving || !formData.title}
                >
                  <Sparkles className="mr-2 h-4 w-4" />
                  AI Regenerate
                </Button>
              </div>
              <Textarea
                id="description"
                name="description"
                placeholder="Describe your item in detail..."
                rows={6}
                value={formData.description}
                onChange={handleInputChange}
                required
              />
            </div>

            {/* Price */}
            <div className="space-y-2">
              <Label htmlFor="price">
                Price <span className="text-red-500">*</span>
              </Label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">
                  $
                </span>
                <Input
                  id="price"
                  name="price"
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                  className="pl-7"
                  value={formData.price}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            {/* Category */}
            <div className="space-y-2">
              <Label htmlFor="category">Category</Label>
              <Select
                value={formData.category}
                onValueChange={(value) =>
                  setFormData(prev => ({ ...prev, category: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a category" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((cat) => (
                    <SelectItem key={cat} value={cat}>
                      {cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Location */}
            <div className="space-y-2">
              <Label htmlFor="location">Location</Label>
              <Input
                id="location"
                name="location"
                placeholder="e.g., Phoenix, AZ"
                value={formData.location}
                onChange={handleInputChange}
              />
            </div>

            {/* Status */}
            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Select
                value={formData.status}
                onValueChange={(value) =>
                  setFormData(prev => ({ ...prev, status: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="draft">Draft</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="paused">Paused</SelectItem>
                  <SelectItem value="sold">Sold</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Images */}
            <div className="space-y-2">
              <Label>Images</Label>
              <div className="space-y-2">
                {formData.images.map((url, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <Input value={url} readOnly />
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => handleImageRemove(index)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleImageAdd}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Add Image URL
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Platforms */}
        <Card>
          <CardHeader>
            <CardTitle>Target Platforms</CardTitle>
            <CardDescription>
              Select platforms for this ad
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {platforms.map((platform) => (
                <div
                  key={platform.id}
                  className={`flex items-center space-x-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors ${
                    formData.platforms.includes(platform.id)
                      ? "border-blue-500 bg-blue-50"
                      : ""
                  }`}
                  onClick={() => handlePlatformToggle(platform.id)}
                >
                  <Checkbox
                    checked={formData.platforms.includes(platform.id)}
                    onCheckedChange={() => handlePlatformToggle(platform.id)}
                  />
                  <span className="text-2xl">{platform.icon}</span>
                  <span className="font-medium">{platform.name}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Save Button */}
        <div className="flex gap-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate("/marketplace/my-ads")}
            disabled={saving}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            className="bg-blue-600 hover:bg-blue-700"
            disabled={saving}
          >
            {saving ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                Save Changes
              </>
            )}
          </Button>
        </div>
      </form>

      {/* Post to Platforms Dialog */}
      <AlertDialog open={showPostDialog} onOpenChange={setShowPostDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Post to Platforms</AlertDialogTitle>
            <AlertDialogDescription>
              Select which platforms you want to post this ad to. Make sure you've connected these platforms first.
            </AlertDialogDescription>
          </AlertDialogHeader>

          <div className="space-y-2 my-4">
            {platforms.map((platform) => (
              <div
                key={platform.id}
                className={`flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 ${
                  selectedPlatformsToPost.includes(platform.id)
                    ? "border-blue-500 bg-blue-50"
                    : ""
                }`}
                onClick={() => {
                  setSelectedPlatformsToPost(prev =>
                    prev.includes(platform.id)
                      ? prev.filter(p => p !== platform.id)
                      : [...prev, platform.id]
                  );
                }}
              >
                <Checkbox
                  checked={selectedPlatformsToPost.includes(platform.id)}
                />
                <span className="text-xl">{platform.icon}</span>
                <span className="font-medium">{platform.name}</span>
              </div>
            ))}
          </div>

          <AlertDialogFooter>
            <AlertDialogCancel disabled={posting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handlePostToPlatforms}
              disabled={posting || selectedPlatformsToPost.length === 0}
              className="bg-green-600 hover:bg-green-700"
            >
              {posting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Posting...
                </>
              ) : (
                <>
                  <Send className="mr-2 h-4 w-4" />
                  Post to {selectedPlatformsToPost.length} Platform(s)
                </>
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default EditAd;
