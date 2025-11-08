package com.crosspostme.data.api

import com.crosspostme.data.model.*
import retrofit2.Response
import retrofit2.http.*

/**
 * API Service for Ads - matches backend routes from Copilot instructions
 * Following the backend API patterns: /api/ads prefix, REST conventions
 */
interface AdsApiService {
    
    // Create Ad - POST /api/ads/
    @POST("api/ads/")
    suspend fun createAd(@Body ad: AdCreate): Response<Ad>
    
    // Get All Ads - GET /api/ads/
    @GET("api/ads/")
    suspend fun getAds(
        @Query("status") status: String? = null,
        @Query("platform") platform: String? = null
    ): Response<List<Ad>>
    
    // Get Ad by ID - GET /api/ads/{ad_id}
    @GET("api/ads/{ad_id}")
    suspend fun getAd(@Path("ad_id") adId: String): Response<Ad>
    
    // Update Ad - PUT /api/ads/{ad_id}
    @PUT("api/ads/{ad_id}")
    suspend fun updateAd(
        @Path("ad_id") adId: String,
        @Body adUpdate: AdUpdate
    ): Response<Ad>
    
    // Delete Ad - DELETE /api/ads/{ad_id}
    @DELETE("api/ads/{ad_id}")
    suspend fun deleteAd(@Path("ad_id") adId: String): Response<Map<String, String>>
    
    // Post Ad to Platform - POST /api/ads/{ad_id}/post
    @POST("api/ads/{ad_id}/post")
    suspend fun postAd(
        @Path("ad_id") adId: String,
        @Query("platform") platform: String
    ): Response<PostedAd>
    
    // Post Ad to Multiple Platforms - POST /api/ads/{ad_id}/post-multiple
    @POST("api/ads/{ad_id}/post-multiple")
    suspend fun postAdMultiplePlatforms(
        @Path("ad_id") adId: String,
        @Body platforms: List<String>
    ): Response<Map<String, Any>>
    
    // Get Posted Ads - GET /api/ads/{ad_id}/posts
    @GET("api/ads/{ad_id}/posts")
    suspend fun getPostedAds(@Path("ad_id") adId: String): Response<List<PostedAd>>
    
    // Get All Posted Ads - GET /api/ads/posted/all
    @GET("api/ads/posted/all")
    suspend fun getAllPostedAds(
        @Query("platform") platform: String? = null
    ): Response<List<PostedAd>>
    
    // Get Dashboard Stats - GET /api/ads/dashboard/stats
    @GET("api/ads/dashboard/stats")
    suspend fun getDashboardStats(): Response<DashboardStats>
    
    // Get Ad Analytics - GET /api/ads/{ad_id}/analytics
    @GET("api/ads/{ad_id}/analytics")
    suspend fun getAdAnalytics(
        @Path("ad_id") adId: String,
        @Query("days") days: Int = 7
    ): Response<List<AdAnalytics>>
}