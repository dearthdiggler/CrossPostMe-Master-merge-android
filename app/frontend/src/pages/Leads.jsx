import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../components/ui/dialog";
import { Textarea } from "../components/ui/textarea";
import {
  Users,
  Search,
  MessageSquare,
  Mail,
  Phone,
  DollarSign,
  Calendar,
  Filter,
  Loader2,
  ExternalLink,
  CheckCircle2,
  XCircle,
  Clock,
  Star,
  Archive,
} from "lucide-react";
import { api } from "../lib/api";

const Leads = () => {
  const navigate = useNavigate();
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [platformFilter, setPlatformFilter] = useState("all");
  const [selectedLead, setSelectedLead] = useState(null);
  const [showDetailDialog, setShowDetailDialog] = useState(false);
  const [showReplyDialog, setShowReplyDialog] = useState(false);
  const [replyMessage, setReplyMessage] = useState("");
  const [replying, setReplying] = useState(false);

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    try {
      setLoading(true);
      const data = await api.get("/api/leads/");
      setLeads(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error fetching leads:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (leadId, newStatus) => {
    try {
      await api.put(`/api/leads/${leadId}`, { status: newStatus });
      setLeads(
        leads.map((lead) =>
          lead.id === leadId ? { ...lead, status: newStatus } : lead
        )
      );
    } catch (err) {
      console.error("Error updating lead status:", err);
    }
  };

  const handleReply = async () => {
    if (!selectedLead || !replyMessage.trim()) return;

    try {
      setReplying(true);
      await api.post(`/api/leads/${selectedLead.id}/reply`, {
        message: replyMessage,
      });

      setShowReplyDialog(false);
      setReplyMessage("");
      await fetchLeads();
    } catch (err) {
      console.error("Error sending reply:", err);
    } finally {
      setReplying(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      new: { color: "bg-blue-100 text-blue-800", label: "New" },
      contacted: { color: "bg-yellow-100 text-yellow-800", label: "Contacted" },
      qualified: { color: "bg-purple-100 text-purple-800", label: "Qualified" },
      negotiating: {
        color: "bg-orange-100 text-orange-800",
        label: "Negotiating",
      },
      converted: { color: "bg-green-100 text-green-800", label: "Sold" },
      lost: { color: "bg-red-100 text-red-800", label: "Lost" },
      archived: { color: "bg-gray-100 text-gray-800", label: "Archived" },
    };

    const config = statusConfig[status] || statusConfig.new;
    return (
      <Badge className={config.color}>
        {config.label}
      </Badge>
    );
  };

  const getPlatformIcon = (platform) => {
    const icons = {
      facebook: "📘",
      ebay: "🛒",
      offerup: "📱",
      craigslist: "📝",
    };
    return icons[platform] || "🔗";
  };

  const filteredLeads = leads.filter((lead) => {
    const matchesSearch =
      lead.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lead.message?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lead.email?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus =
      statusFilter === "all" || lead.status === statusFilter;
    const matchesPlatform =
      platformFilter === "all" || lead.platform === platformFilter;

    return matchesSearch && matchesStatus && matchesPlatform;
  });

  const stats = {
    total: leads.length,
    new: leads.filter((l) => l.status === "new").length,
    qualified: leads.filter((l) => l.status === "qualified").length,
    converted: leads.filter((l) => l.status === "converted").length,
  };

  if (loading) {
    return (
      <div className="flex-1 space-y-4 p-8 pt-6">
        <h2 className="text-3xl font-bold tracking-tight">Leads</h2>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">Leads</h2>
        <Button onClick={fetchLeads}>
          <Users className="mr-2 h-4 w-4" />
          Refresh
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Leads</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">New Leads</CardTitle>
            <MessageSquare className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats.new}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Qualified</CardTitle>
            <Star className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">
              {stats.qualified}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Converted</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {stats.converted}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search leads by name, email, or message..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full md:w-48">
                <Filter className="mr-2 h-4 w-4" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="new">New</SelectItem>
                <SelectItem value="contacted">Contacted</SelectItem>
                <SelectItem value="qualified">Qualified</SelectItem>
                <SelectItem value="negotiating">Negotiating</SelectItem>
                <SelectItem value="converted">Converted</SelectItem>
                <SelectItem value="lost">Lost</SelectItem>
              </SelectContent>
            </Select>

            <Select value={platformFilter} onValueChange={setPlatformFilter}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue />
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

      {/* Leads List */}
      <div className="space-y-4">
        {filteredLeads.length === 0 ? (
          <Card>
            <CardContent className="pt-12 pb-12 text-center">
              <Users className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                No leads found
              </h3>
              <p className="text-gray-600 mb-4">
                {searchTerm || statusFilter !== "all" || platformFilter !== "all"
                  ? "Try adjusting your filters"
                  : "Leads will appear here when buyers contact you"}
              </p>
            </CardContent>
          </Card>
        ) : (
          filteredLeads.map((lead) => (
            <Card key={lead.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                  <div className="flex-1 space-y-3">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="text-lg font-semibold">
                            {lead.name || "Anonymous"}
                          </h3>
                          {getStatusBadge(lead.status)}
                          <span className="text-2xl">
                            {getPlatformIcon(lead.platform)}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600">
                          For: <strong>{lead.ad_title}</strong>
                        </p>
                      </div>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-sm text-gray-800">{lead.message}</p>
                    </div>

                    <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                      {lead.email && (
                        <div className="flex items-center gap-1">
                          <Mail className="h-4 w-4" />
                          <span>{lead.email}</span>
                        </div>
                      )}
                      {lead.phone && (
                        <div className="flex items-center gap-1">
                          <Phone className="h-4 w-4" />
                          <span>{lead.phone}</span>
                        </div>
                      )}
                      {lead.offer_amount && (
                        <div className="flex items-center gap-1 text-green-600 font-medium">
                          <DollarSign className="h-4 w-4" />
                          <span>${lead.offer_amount}</span>
                        </div>
                      )}
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        <span>
                          {new Date(lead.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col gap-2">
                    <Select
                      value={lead.status}
                      onValueChange={(value) =>
                        handleStatusChange(lead.id, value)
                      }
                    >
                      <SelectTrigger className="w-full md:w-48">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="new">New</SelectItem>
                        <SelectItem value="contacted">Contacted</SelectItem>
                        <SelectItem value="qualified">Qualified</SelectItem>
                        <SelectItem value="negotiating">Negotiating</SelectItem>
                        <SelectItem value="converted">Converted</SelectItem>
                        <SelectItem value="lost">Lost</SelectItem>
                        <SelectItem value="archived">Archived</SelectItem>
                      </SelectContent>
                    </Select>

                    <Button
                      onClick={() => {
                        setSelectedLead(lead);
                        setShowReplyDialog(true);
                      }}
                      className="w-full"
                    >
                      <MessageSquare className="mr-2 h-4 w-4" />
                      Reply
                    </Button>

                    <Button
                      variant="outline"
                      onClick={() => {
                        setSelectedLead(lead);
                        setShowDetailDialog(true);
                      }}
                      className="w-full"
                    >
                      View Details
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Reply Dialog */}
      <Dialog open={showReplyDialog} onOpenChange={setShowReplyDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reply to {selectedLead?.name}</DialogTitle>
            <DialogDescription>
              Send a message to this lead about {selectedLead?.ad_title}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-sm text-gray-600 mb-1">Original Message:</p>
              <p className="text-sm text-gray-800">{selectedLead?.message}</p>
            </div>

            <div className="space-y-2">
              <Textarea
                value={replyMessage}
                onChange={(e) => setReplyMessage(e.target.value)}
                placeholder="Type your reply..."
                rows={6}
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowReplyDialog(false)}
              disabled={replying}
            >
              Cancel
            </Button>
            <Button
              onClick={handleReply}
              disabled={replying || !replyMessage.trim()}
            >
              {replying ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Sending...
                </>
              ) : (
                <>
                  <MessageSquare className="mr-2 h-4 w-4" />
                  Send Reply
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Detail Dialog */}
      <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Lead Details</DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Name:</p>
              <p className="text-base">{selectedLead?.name || "Not provided"}</p>
            </div>

            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Email:</p>
              <p className="text-base">{selectedLead?.email || "Not provided"}</p>
            </div>

            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Phone:</p>
              <p className="text-base">{selectedLead?.phone || "Not provided"}</p>
            </div>

            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">
                Platform:
              </p>
              <p className="text-base capitalize">{selectedLead?.platform}</p>
            </div>

            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Status:</p>
              {selectedLead && getStatusBadge(selectedLead.status)}
            </div>

            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Message:</p>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-sm">{selectedLead?.message}</p>
              </div>
            </div>

            {selectedLead?.offer_amount && (
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Offer:</p>
                <p className="text-lg font-semibold text-green-600">
                  ${selectedLead.offer_amount}
                </p>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button onClick={() => setShowDetailDialog(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Leads;
